import os
import json
import toml
import importlib.util
import time
from collections import defaultdict
from tabulate import tabulate

SYSTEM_MESSAGE_FILE = "system_messages.toml"


def read_jsonl(file_path):
    """
    Reads a JSONL file and returns a list of dictionaries.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def read_toml(file_path):
    """
    Reads a TOML file and returns its parsed content.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return toml.load(f)


def get_system_message(system_message_config, spotlighting_data_marker):
    """
    Retrieves the appropriate system message from the system_message_config
    based on a given spotlighting data marker. Falls back to 'default' if no
    exact match is found.
    """
    if system_message_config is None:
        return None

    for config in system_message_config["configurations"]:
        if config["spotlighting_data_markers"] == spotlighting_data_marker:
            return config["system_message"]
    for config in system_message_config["configurations"]:
        if config["spotlighting_data_markers"] == "default":
            return config["system_message"]

    return None


def substitute_instruction(jailbreak_text, instruction_text):
    """
    Replaces <INSTRUCTION> in the jailbreak text with the given instruction text.
    """
    if "<INSTRUCTION>" in jailbreak_text:
        return jailbreak_text.replace("<INSTRUCTION>", instruction_text)
    return jailbreak_text


def find_nearest_whitespace(text, index):
    """
    Finds the nearest whitespace character to the given index in the text.
    Returns the index of that whitespace character (or original index if none found).
    """
    forward_index = text.find(' ', index)
    backward_index = text.rfind(' ', 0, index)

    if forward_index == -1 and backward_index == -1:
        return index
    elif forward_index == -1:
        return backward_index
    elif backward_index == -1:
        return forward_index
    else:
        return forward_index if abs(forward_index - index) < abs(index - backward_index) else backward_index


def insert_jailbreak(document, combined_text, position, injection_pattern):
    """
    Inserts the combined_text into the document at the specified position
    using the provided injection_pattern. The pattern must contain the
    placeholder 'INJECTION_PAYLOAD'.
    """
    if 'INJECTION_PAYLOAD' not in injection_pattern:
        raise ValueError("Injection pattern must contain 'INJECTION_PAYLOAD' placeholder.")
    injected_text = injection_pattern.replace('INJECTION_PAYLOAD', combined_text)

    if position == 'start':
        return f"{injected_text}{document}"
    elif position == 'middle':
        mid_point = len(document) // 2
        insert_index = find_nearest_whitespace(document, mid_point)
        return f"{document[:insert_index]}{injected_text}{document[insert_index:]}"
    elif position == 'end':
        return f"{document}{injected_text}"
    else:
        raise ValueError(f"Invalid position: {position}")


def load_plugins(plugin_names):
    """
    For each plugin name, try:
      1) <cwd>/plugins/<name>.py
      2) built-in package plugin (spikee.plugins.<name>)
    If found, dynamically import and return it.
    """
    plugins = []
    for name in plugin_names:
        # 1) Check local
        local_path = os.path.join(os.getcwd(), 'plugins', f'{name}.py')
        if os.path.isfile(local_path):
            mod = load_plugin_from_path(local_path, name)
            if mod:
                plugins.append((name, mod))
                continue
        
        # 2) Check built-in
        try:
            # e.g. "spikee.plugins.name"
            builtin_module = importlib.import_module(f"spikee.plugins.{name}")
            plugins.append((name, builtin_module))
            continue
        except ModuleNotFoundError:
            pass
        
        print(f"Warning: Plugin '{name}' not found locally or in built-in plugins.")
    return plugins

def load_plugin_from_path(plugin_path, plugin_name):
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    if spec and spec.loader:
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        return plugin_module
    else:
        return None

def apply_plugin(plugin_module, text):
    """
    Applies a plugin module's transform function to the given text if available.
    """
    if hasattr(plugin_module, 'transform'):
        return plugin_module.transform(text)
    print(f"Plugin '{plugin_module.__name__}' does not have a 'transform' function.")
    return text


def process_standalone_attacks(standalone_attacks, dataset, entry_id, output_format='full-prompt'):
    """
    Processes standalone attacks and appends them to the dataset.
    Returns the updated dataset and the next entry_id.
    """
    for attack in standalone_attacks:
        attack_id = attack['id']
        text = attack['text']
        canary = attack.get('canary', '')
        jailbreak_type = attack.get('jailbreak_type', '')
        instruction_type = attack.get('instruction_type', '')
        lang = attack.get('lang', 'en')

        entry = {
            "id": entry_id,
            "long_id": attack_id,
            "text": text,
            "canary": canary,
            "injected": "true",
            "jailbreak_type": jailbreak_type,
            "instruction_type": instruction_type,
            "task_type": None,
            "document_id": None,
            "position": None,
            "spotlighting_data_markers": None,
            "injection_delimiters": None,
            "lang": lang,
            "suffix_id": None
        }
        dataset.append(entry)
        entry_id += 1

    return dataset, entry_id


def write_jsonl(data, output_file):
    """
    Writes a list of dictionaries to a JSONL file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')


def _create_summary_entry(entry_id, base_id, jailbreak_id, instruction_id, position,
                          plugin_suffix, wrapped_document, canary, ideal_summary,
                          jailbreak_type, instruction_type, injection_pattern,
                          spotlighting_data_marker, lang, suffix_id, system_message, plugin_name):
    """
    Creates a dictionary for a 'summarization' entry in a full-prompt format.
    """
    summary_entry = {
        "id": entry_id,
        "long_id": f"summary_{base_id}_{jailbreak_id}_{instruction_id}_{position}{plugin_suffix}",
        "text": f"Summarize the following document:\n{wrapped_document}",
        "canary": canary,
        "injected": "true",
        "ideal_answer": ideal_summary,
        "task_type": "summarization",
        "jailbreak_type": jailbreak_type,
        "instruction_type": instruction_type,
        "document_id": base_id,
        "position": position,
        "spotlighting_data_markers": spotlighting_data_marker,
        "injection_delimiters": injection_pattern,
        "lang": lang,
        "suffix_id": suffix_id,
        "system_message": system_message,
        "plugin": plugin_name
    }
    if suffix_id:
        summary_entry["long_id"] += f"-{suffix_id}"
    if system_message:
        summary_entry["long_id"] += "-sys"
    return summary_entry


def _create_qa_entry(entry_id, base_id, jailbreak_id, instruction_id, position,
                     plugin_suffix, wrapped_document, canary, question, ideal_answer,
                     jailbreak_type, instruction_type, injection_pattern,
                     spotlighting_data_marker, lang, suffix_id, system_message, plugin_name):
    """
    Creates a dictionary for a 'qna' entry in a full-prompt format.
    """
    qa_entry = {
        "id": entry_id,
        "long_id": f"qa_{base_id}_{jailbreak_id}_{instruction_id}_{position}{plugin_suffix}",
        "text": f"Given this document:\n{wrapped_document}\nAnswer the following question: {question}",
        "canary": canary,
        "injected": "true",
        "ideal_answer": ideal_answer,
        "task_type": "qna",
        "jailbreak_type": jailbreak_type,
        "instruction_type": instruction_type,
        "document_id": base_id,
        "position": position,
        "spotlighting_data_markers": spotlighting_data_marker,
        "injection_delimiters": injection_pattern,
        "lang": lang,
        "suffix_id": suffix_id,
        "system_message": system_message,
        "plugin": plugin_name
    }
    if suffix_id:
        qa_entry["long_id"] += f"-{suffix_id}"
    if system_message:
        qa_entry["long_id"] += "-sys"
    return qa_entry


def _create_document_entry(entry_id, base_id, jailbreak_id, instruction_id, position,
                           plugin_suffix, modified_document, canary, jailbreak_type,
                           instruction_type, injection_pattern, spotlighting_data_marker,
                           lang, suffix_id, system_message, plugin_name, output_format):
    """
    Creates a dictionary for a 'document' entry when output_format == 'document'.
    """
    doc_entry = {
        "id": entry_id,
        "long_id": f"{output_format}_{base_id}_{jailbreak_id}_{instruction_id}_{position}{plugin_suffix}",
        "text": modified_document,
        "canary": canary,
        "injected": "true",
        "jailbreak_type": jailbreak_type,
        "instruction_type": instruction_type,
        "task_type": None,
        "document_id": base_id,
        "position": position,
        "spotlighting_data_markers": spotlighting_data_marker,
        "injection_delimiters": injection_pattern,
        "lang": lang,
        "suffix_id": suffix_id,
        "system_message": system_message,
        "plugin": plugin_name
    }
    if suffix_id:
        doc_entry["long_id"] += f"-{suffix_id}"
    if system_message:
        doc_entry["long_id"] += "-sys"
    return doc_entry


def generate_variations(base_docs, jailbreaks, instructions, positions, injection_delimiters,
                        spotlighting_data_markers_list, plugins, adv_suffixes=None,
                        output_format='full-prompt', match_languages=False,
                        system_message_config=None):
    """
    Generates dataset variations from the given base documents, jailbreaks,
    instructions, injection positions, delimiters, data markers, and plugins.
    Returns the dataset and the last used entry_id.
    """
    dataset = []
    entry_id = 1

    suffixes = [None] + adv_suffixes if adv_suffixes else [None]

    for base_doc in base_docs:
        base_id = base_doc['id']
        document = base_doc['document']
        question = base_doc.get('question', '')
        ideal_answer = base_doc.get('ideal_answer', '')
        ideal_summary = base_doc.get('ideal_summary', '')

        for jailbreak in jailbreaks:
            jailbreak_id = jailbreak['id']
            jailbreak_text = jailbreak['text']
            jailbreak_canary = jailbreak.get('canary', '')
            jailbreak_type = jailbreak.get('jailbreak_type', '')
            jailbreak_lang = jailbreak.get('lang', 'en')

            for instruction in instructions:
                instruction_id = instruction['id']
                instruction_text = instruction['instruction']
                instruction_canary = instruction.get('canary', '')
                instruction_type = instruction.get('instruction_type', '')
                instruction_lang = instruction.get('lang', 'en')

                if match_languages and jailbreak_lang != instruction_lang:
                    continue

                if "<INSTRUCTION>" in jailbreak_text:
                    combined_text = substitute_instruction(jailbreak_text, instruction_text)
                    canary = instruction_canary
                    lang = instruction_lang
                else:
                    combined_text = jailbreak_text
                    canary = jailbreak_canary
                    lang = jailbreak_lang

                # 1) No-plugin entries
                for suffix in suffixes:
                    modified_combined_text = combined_text
                    suffix_id = None
                    if suffix:
                        modified_combined_text += " " + suffix['suffix']
                        suffix_id = suffix['id']

                    for position in positions:
                        for injection_pattern in injection_delimiters:
                            injected_doc = insert_jailbreak(
                                document, modified_combined_text, position, injection_pattern
                            )

                            if output_format == 'burp':
                                burp_payload_encoded = json.dumps(injected_doc)[1:-1]
                                dataset.append(burp_payload_encoded)
                            else:
                                for spotlighting_data_marker in spotlighting_data_markers_list:
                                    if output_format == 'full-prompt':
                                        wrapped_document = (
                                            injected_doc if spotlighting_data_marker == 'none'
                                            else spotlighting_data_marker.replace('DOCUMENT', injected_doc)
                                        )

                                        system_message = get_system_message(
                                            system_message_config, spotlighting_data_marker
                                        )

                                        summary_entry = _create_summary_entry(
                                            entry_id, base_id, jailbreak_id, instruction_id,
                                            position, '', wrapped_document, canary, ideal_summary,
                                            jailbreak_type, instruction_type, injection_pattern,
                                            spotlighting_data_marker, lang, suffix_id, system_message, None
                                        )
                                        dataset.append(summary_entry)
                                        entry_id += 1

                                        qa_entry = _create_qa_entry(
                                            entry_id, base_id, jailbreak_id, instruction_id,
                                            position, '', wrapped_document, canary, question,
                                            ideal_answer, jailbreak_type, instruction_type,
                                            injection_pattern, spotlighting_data_marker, lang,
                                            suffix_id, system_message, None
                                        )
                                        dataset.append(qa_entry)
                                        entry_id += 1

                                    elif output_format == 'document':
                                        system_message = None
                                        doc_entry = _create_document_entry(
                                            entry_id, base_id, jailbreak_id, instruction_id,
                                            position, '', injected_doc, canary, jailbreak_type,
                                            instruction_type, injection_pattern,
                                            spotlighting_data_marker, lang, suffix_id,
                                            system_message, None, output_format
                                        )
                                        dataset.append(doc_entry)
                                        entry_id += 1

                # 2) Plugin entries
                for plugin_name, plugin_module in plugins:
                    for suffix in suffixes:
                        plugin_modified_text = apply_plugin(plugin_module, combined_text)
                        suffix_id = None
                        if suffix:
                            plugin_modified_text += " " + suffix['suffix']
                            suffix_id = suffix['id']

                        for position in positions:
                            for injection_pattern in injection_delimiters:
                                injected_doc = insert_jailbreak(
                                    document, plugin_modified_text, position, injection_pattern
                                )

                                if output_format == 'burp':
                                    burp_payload_encoded = json.dumps(injected_doc)[1:-1]
                                    dataset.append(burp_payload_encoded)
                                else:
                                    for spotlighting_data_marker in spotlighting_data_markers_list:
                                        if output_format == 'full-prompt':
                                            wrapped_document = (
                                                injected_doc if spotlighting_data_marker == 'none'
                                                else spotlighting_data_marker.replace('DOCUMENT', injected_doc)
                                            )

                                            system_message = get_system_message(
                                                system_message_config, spotlighting_data_marker
                                            )

                                            summary_entry = _create_summary_entry(
                                                entry_id, base_id, jailbreak_id, instruction_id,
                                                position, f"_{plugin_name}", wrapped_document, canary,
                                                ideal_summary, jailbreak_type, instruction_type,
                                                injection_pattern, spotlighting_data_marker, lang,
                                                suffix_id, system_message, plugin_name
                                            )
                                            dataset.append(summary_entry)
                                            entry_id += 1

                                            qa_entry = _create_qa_entry(
                                                entry_id, base_id, jailbreak_id, instruction_id,
                                                position, f"_{plugin_name}", wrapped_document, canary,
                                                question, ideal_answer, jailbreak_type,
                                                instruction_type, injection_pattern,
                                                spotlighting_data_marker, lang, suffix_id,
                                                system_message, plugin_name
                                            )
                                            dataset.append(qa_entry)
                                            entry_id += 1

                                        elif output_format == 'document':
                                            system_message = get_system_message(
                                                system_message_config, spotlighting_data_marker
                                            )
                                            doc_entry = _create_document_entry(
                                                entry_id, base_id, jailbreak_id, instruction_id,
                                                position, f"_{plugin_name}", injected_doc, canary,
                                                jailbreak_type, instruction_type, injection_pattern,
                                                spotlighting_data_marker, lang, suffix_id,
                                                system_message, plugin_name, output_format
                                            )
                                            dataset.append(doc_entry)
                                            entry_id += 1

    return dataset, entry_id

def resolve_seed_folder(seed_folder_name):
    """
    Return the absolute path to the seed folder, searching local workspace first,
    then built-in package data.
    """
    local_path = os.path.join(os.getcwd(), "datasets", seed_folder_name)
    if os.path.isdir(local_path):
        return local_path

    # built-in path
    builtin_path = os.path.join(os.path.dirname(__file__), "data", seed_folder_name)
    if os.path.isdir(builtin_path):
        return builtin_path

    # Fallback: raise error
    raise FileNotFoundError(f"Seed folder '{seed_folder_name}' not found "
                            f"in local datasets/ or in built-in spikee/data/")

def generate_dataset(args):
    """
    Main entry point for generating the dataset. Loads files, filters content,
    generates variations, writes results to disk, and prints stats.
    """
    seed_folder = resolve_seed_folder(args.seed_folder)     
    output_format = args.format
    injection_delimiters_input = args.injection_delimiters
    spotlighting_data_markers_input = args.spotlighting_data_markers
    include_system_message = args.include_system_message

    injection_delimiters = [
        delim.encode('utf-8').decode('unicode_escape')
        for delim in injection_delimiters_input.split(',')
    ]
    spotlighting_data_markers_list = [
        marker.encode('utf-8').decode('unicode_escape')
        for marker in spotlighting_data_markers_input.split(',')
    ]

    languages_input = args.languages
    match_languages = args.match_languages
    instruction_filter_input = args.instruction_filter
    jailbreak_filter_input = args.jailbreak_filter
    include_suffixes = args.include_suffixes

    if languages_input:
        languages = [lang.strip() for lang in languages_input.split(',')]
    else:
        languages = None

    if instruction_filter_input:
        instruction_filters = [i.strip() for i in instruction_filter_input.split(',')]
    else:
        instruction_filters = None

    if jailbreak_filter_input:
        jailbreak_filters = [j.strip() for j in jailbreak_filter_input.split(',')]
    else:
        jailbreak_filters = None

    base_documents_file = os.path.join(seed_folder, 'base_documents.jsonl')
    jailbreaks_file = os.path.join(seed_folder, 'jailbreaks.jsonl')
    instructions_file = os.path.join(seed_folder, 'instructions.jsonl')
    adv_suffixes_file = os.path.join(seed_folder, 'adv_suffixes.jsonl')

    required_files = [base_documents_file, jailbreaks_file, instructions_file]
    if include_suffixes:
        required_files.append(adv_suffixes_file)

    for file_path in required_files:
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            return

    base_docs = read_jsonl(base_documents_file)
    jailbreaks = read_jsonl(jailbreaks_file)
    instructions = read_jsonl(instructions_file)
    adv_suffixes = read_jsonl(adv_suffixes_file) if include_suffixes else None

    processed_jailbreaks = []
    for jb in jailbreaks:
        jb_lang = jb.get('lang', 'en')
        jb['lang'] = jb_lang
        jb_type = jb.get('jailbreak_type', '')
        if languages and jb_lang not in languages:
            continue
        if jailbreak_filters and jb_type not in jailbreak_filters:
            continue
        processed_jailbreaks.append(jb)
    jailbreaks = processed_jailbreaks

    processed_instructions = []
    for instr in instructions:
        instr_lang = instr.get('lang', 'en')
        instr['lang'] = instr_lang
        instr_type = instr.get('instruction_type', '')
        if languages and instr_lang not in languages:
            continue
        if instruction_filters and instr_type not in instruction_filters:
            continue
        processed_instructions.append(instr)
    instructions = processed_instructions

    plugins = load_plugins(args.plugins)
    system_message_config = read_toml(SYSTEM_MESSAGE_FILE) if include_system_message else None

    dataset, entry_id = generate_variations(
        base_docs,
        jailbreaks,
        instructions,
        args.positions,
        injection_delimiters,
        spotlighting_data_markers_list,
        plugins,
        adv_suffixes=adv_suffixes,
        output_format=output_format,
        match_languages=match_languages,
        system_message_config=system_message_config
    )

    if args.standalone_attacks:
        if not os.path.isfile(args.standalone_attacks):
            print(f"Error: File not found: {args.standalone_attacks}")
            return
        standalone_attacks = read_jsonl(args.standalone_attacks)
        dataset, entry_id = process_standalone_attacks(
            standalone_attacks, dataset, entry_id, output_format=output_format
        )

    timestamp = int(time.time())
    seed_folder_name = os.path.basename(os.path.normpath(seed_folder))
    output_file_name = f"{timestamp}-{seed_folder_name}-{output_format}"
    if include_system_message:
        output_file_name += "-sys"
    output_file_path = os.path.join('datasets', output_file_name)

    if output_format == 'burp':
        output_file_path += "-dataset.txt"
        os.makedirs('datasets', exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for payload in dataset:
                f.write(payload + '\n')
    else:
        output_file_path += "-dataset.jsonl"
        os.makedirs('datasets', exist_ok=True)
        write_jsonl(dataset, output_file_path)

    print(f"Dataset generated and saved to {output_file_path}")

    stats = {
        'total_entries': len(dataset),
        'by_jailbreak_type': defaultdict(int),
        'by_instruction_type': defaultdict(int),
        'by_lang': defaultdict(int),
        'by_task_type': defaultdict(int),
        'by_suffix_id': defaultdict(int),
        'by_plugin_id': defaultdict(int)
    }

    for entry in dataset:
        if isinstance(entry, str):
            continue
        jb_type = entry.get('jailbreak_type') or 'None'
        instr_type = entry.get('instruction_type') or 'None'
        lang = entry.get('lang', 'en')
        task_type = entry.get('task_type') or 'None'
        suffix_id = entry.get('suffix_id') or 'None'
        plugin_id = entry.get('plugin') or 'None'

        stats['by_jailbreak_type'][jb_type] += 1
        stats['by_instruction_type'][instr_type] += 1
        stats['by_lang'][lang] += 1
        stats['by_task_type'][task_type] += 1
        stats['by_suffix_id'][suffix_id] += 1
        stats['by_plugin_id'][plugin_id] += 1

    print("\n=== Dataset Statistics ===")
    print(f"Total Entries: {stats['total_entries']}")

    def print_stats(title, data):
        print(f"\nBreakdown by {title}:")
        table = []
        for key, count in data.items():
            display_key = key if key else 'None'
            table.append([display_key, count])
        print(tabulate(table, headers=[title, 'Count']))

    print_stats('Jailbreak Type', stats['by_jailbreak_type'])
    print_stats('Instruction Type', stats['by_instruction_type'])
    print_stats('Language', stats['by_lang'])
    print_stats('Task Type', stats['by_task_type'])
    print_stats('Suffix ID', stats['by_suffix_id'])
    print_stats('Plugin ID', stats['by_plugin_id'])
