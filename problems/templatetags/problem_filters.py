from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def parse_problem_description(description):
    """
    Parse problem description and convert it to LeetCode-style HTML format.
    This filter will automatically detect and format:
    - Examples with Input/Output/Explanation
    - Constraints
    - Follow-up questions
    """
    if not description:
        return ""
    
    # Convert to string if it's not already
    description = str(description)
    
    # Split the description into sections
    sections = description.split('\n\n')
    
    html_parts = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check if this is an example section
        if re.match(r'^Example\s+\d+:', section, re.IGNORECASE):
            html_parts.append(parse_example_section(section))
        # Check if this is a constraints section
        elif re.match(r'^Constraints?:', section, re.IGNORECASE):
            html_parts.append(parse_constraints_section(section))
        # Check if this is a follow-up section
        elif re.match(r'^Follow.?up:', section, re.IGNORECASE):
            html_parts.append(parse_followup_section(section))
        # Regular description text
        else:
            html_parts.append(f'<div class="problem-description-text">{section}</div>')
    
    return mark_safe('\n'.join(html_parts))

def parse_example_section(section):
    """Parse an example section and convert it to LeetCode-style HTML."""
    lines = section.split('\n')
    example_title = lines[0].strip()
    
    # Extract example number
    example_num_match = re.search(r'Example\s+(\d+):', example_title, re.IGNORECASE)
    example_num = example_num_match.group(1) if example_num_match else "1"
    
    html = f'''
    <div class="example-card">
        <div class="example-header">
            <span class="example-number">Example {example_num}:</span>
        </div>
        <div class="example-content">
    '''
    
    current_input = ""
    current_output = ""
    current_explanation = ""
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        # Check for input
        if re.match(r'^<b>Input:</b>', line, re.IGNORECASE) or re.match(r'^Input:', line, re.IGNORECASE):
            current_input = extract_content_from_line(line)
        # Check for output
        elif re.match(r'^<b>Output:</b>', line, re.IGNORECASE) or re.match(r'^Output:', line, re.IGNORECASE):
            current_output = extract_content_from_line(line)
        # Check for explanation
        elif re.match(r'^<b>Explanation:</b>', line, re.IGNORECASE) or re.match(r'^Explanation:', line, re.IGNORECASE):
            current_explanation = extract_content_from_line(line)
        # If we're inside a <pre> tag, this might be formatted content
        elif line.startswith('<pre>') or line.endswith('</pre>'):
            # Extract content from pre tags
            pre_content = re.sub(r'<pre>|</pre>', '', line)
            # Parse the pre content for input/output/explanation
            if '<b>Input:</b>' in pre_content:
                current_input = extract_content_from_pre(pre_content, 'Input')
            if '<b>Output:</b>' in pre_content:
                current_output = extract_content_from_pre(pre_content, 'Output')
            if '<b>Explanation:</b>' in pre_content:
                current_explanation = extract_content_from_pre(pre_content, 'Explanation')
    
    # Add input section if found
    if current_input:
        html += f'''
            <div class="example-input">
                <div class="example-label">
                    <i class="fas fa-arrow-right"></i> Input:
                </div>
                <div class="example-code">
                    <code>{current_input}</code>
                </div>
            </div>
        '''
    
    # Add output section if found
    if current_output:
        html += f'''
            <div class="example-output">
                <div class="example-label">
                    <i class="fas fa-arrow-right"></i> Output:
                </div>
                <div class="example-code">
                    <code>{current_output}</code>
                </div>
            </div>
        '''
    
    # Add explanation section if found
    if current_explanation:
        html += f'''
            <div class="example-explanation">
                <div class="example-label">
                    <i class="fas fa-info-circle"></i> Explanation:
                </div>
                <div class="explanation-text">
                    {current_explanation}
                </div>
            </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def parse_constraints_section(section):
    """Parse a constraints section and convert it to LeetCode-style HTML."""
    lines = section.split('\n')
    constraints_content = []
    
    for line in lines[1:]:
        line = line.strip()
        if line:
            # Clean up the constraint text
            constraint = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
            constraint = constraint.replace('le', '≤').replace('ge', '≥')  # Fix common symbols
            if constraint:
                constraints_content.append(f'• {constraint}')
    
    constraints_html = '<br>'.join(constraints_content) if constraints_content else section
    
    return f'''
    <div class="constraints-section">
        <h4 class="section-title">
            <i class="fas fa-shield-alt"></i> Constraints
        </h4>
        <div class="constraints-content">
            {constraints_html}
        </div>
    </div>
    '''

def parse_followup_section(section):
    """Parse a follow-up section and convert it to LeetCode-style HTML."""
    lines = section.split('\n')
    followup_content = ' '.join(lines[1:]).strip()
    
    return f'''
    <div class="follow-up-section">
        <h4 class="section-title">
            <i class="fas fa-lightbulb"></i> Follow up
        </h4>
        <div class="follow-up-content">
            {followup_content}
        </div>
    </div>
    '''

def extract_content_from_line(line):
    """Extract content from a line that might contain HTML tags."""
    # Remove HTML tags and extract content
    content = re.sub(r'<[^>]+>', '', line)
    # Remove the label part (Input:, Output:, etc.)
    content = re.sub(r'^(Input|Output|Explanation):\s*', '', content, flags=re.IGNORECASE)
    return content.strip()

def extract_content_from_pre(pre_content, section_type):
    """Extract content from a <pre> tag for a specific section type."""
    # Look for the specific section in the pre content
    pattern = rf'<b>{section_type}:</b>\s*(.*?)(?=<b>|$)'
    match = re.search(pattern, pre_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

@register.filter
def extract_examples_from_description(description):
    """Extract examples from description and return them as a list."""
    if not description:
        return []
    
    examples = []
    sections = description.split('\n\n')
    
    for section in sections:
        if re.match(r'^Example\s+\d+:', section, re.IGNORECASE):
            examples.append(section)
    
    return examples

@register.filter
def extract_constraints_from_description(description):
    """Extract constraints from description."""
    if not description:
        return ""
    
    sections = description.split('\n\n')
    
    for section in sections:
        if re.match(r'^Constraints?:', section, re.IGNORECASE):
            return section
    
    return ""
