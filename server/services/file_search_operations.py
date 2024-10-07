from io import BytesIO
import re
import os

def extract_sections(file_path, search_terms, sections, specify_lines, use_total_lines, total_lines):
    '''
    Extracts the data from orca log file based on search terms and sections.
    '''
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    document_content = ""
    
    # Define the regex pattern for the header
    header_pattern = r'^\s*NO\s+LB\s+ZA\s+FRAG\s+MASS\s+X\s+Y\s+Z\s*$'
    
    # Function to determine if a line is content
    def is_content_line(line, term, header_pattern=None):
        if line.strip() == "":
            return False
        if line.startswith("-----"):
            return False
        if line.startswith(term):
            return False
        if header_pattern and re.match(header_pattern, line):
            return False
        pattern = r'^\s*(\w+)\s+(\d+)\s+(\d+|\w+)\s+\w+'
        if re.match(pattern, line):
            return False
        return True

    # Function to identify if the line marks the end of a section
    def is_end_pattern(lines, index):
        if index + 2 >= len(lines):
            return False
        return ((lines[index].strip().startswith('-') or lines[index].strip().startswith('*')) and
                (lines[index].strip() in lines[index + 2].strip() or lines[index].strip() in lines[index + 3].strip()) and
                not lines[index + 1].strip().startswith('-'))

    for term in search_terms:
        line_num = 0
        term_line_num = []
        terms_num = 0
        for line in lines:
            if term in line:
                term_line_num.append(line_num)
                print(f"Term: {term}, Line number: {line_num}, term_line_num: {term_line_num}")
                terms_num += 1
            line_num += 1

    search_term = search_terms[0]  #make generic later

    for i in sections:
        section_lines = specify_lines[i-1].split()
        start_line = term_line_num[i-1]
        line_empty = 0
        document_content += lines[start_line]
        print(f"Start line: {start_line}")
        print("document_content: ", document_content)

        if section_lines[0].upper() == 'WHOLE' and not use_total_lines:
            while line_empty == 0:
                if is_end_pattern(lines, start_line):
                    break
                if lines[start_line] != "\n" and is_content_line(lines[start_line], search_term, header_pattern):
                    document_content += lines[start_line]
                    start_line += 1
                else:
                    line_empty = 1

        if section_lines[0].upper() == 'WHOLE' and use_total_lines:
            if is_end_pattern(lines, start_line):
                break
            for _ in range(total_lines - start_line + term_line_num[i-1]):
                if is_content_line(lines[start_line], search_term, header_pattern):
                    document_content += lines[start_line]
                start_line += 1
                line_empty = 1

        elif section_lines[0].upper() == 'FIRST':
            line_count = 0
            while line_count < int(section_lines[1]):
                if is_end_pattern(lines, start_line):
                    break
                if search_term not in lines[start_line].strip() and is_content_line(lines[start_line], search_term, header_pattern):
                    document_content += lines[start_line]
                    line_count += 1
                start_line += 1

        elif section_lines[0].upper() == 'LAST':
            temp_content = []
            while start_line < len(lines):
                if is_end_pattern(lines, start_line):
                    break
                if is_content_line(lines[start_line], search_term, header_pattern):
                    temp_content.append(lines[start_line])
                start_line += 1
            document_content += ''.join(temp_content[-int(section_lines[1]):])

        elif section_lines[0].upper() == 'SPECIFIC':
            specific_lines = [int(l) for l in section_lines[1].split(",")]
            for l in specific_lines:
                if start_line + l < len(lines) and not is_end_pattern(lines, start_line + l):
                    if is_content_line(lines[start_line + l], search_term, header_pattern):
                        document_content += lines[start_line + l]

    return document_content

def save_document_to_bytes(document):
    '''
    Save the Word document to a byte string
    '''
    file_stream = BytesIO()
    document.save(file_stream)
    return file_stream.getvalue()
