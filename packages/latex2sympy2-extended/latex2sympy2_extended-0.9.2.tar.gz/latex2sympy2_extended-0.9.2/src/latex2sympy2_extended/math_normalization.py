import re
from dataclasses import dataclass

@dataclass(frozen=True)
class NormalizationConfig:
    """Configuration for latex normalization.
    
    Each field controls a group of related normalizations:
    - basic_latex: Basic latex command replacements (mathrm, displaystyle, etc.)
    - units: Remove units and their variations
    - malformed_operators: Fix malformed operators (sqrt, frac, etc.)
    - nits: Small formatting fixes (spaces, dots, etc.)
    - boxed: Extract content from boxed environments
    - equations: Handle equation splitting and approximations
    """
    basic_latex: bool
    units: bool
    malformed_operators: bool
    nits: bool
    boxed: bool
    equations: bool

# Compile all regex patterns once at module level
r_left = re.compile(r"\\m?left(\\\{|\{|\\\||\||\[|\(|\\rbracl|\\lgroup|\\lbrace|\\lbrack|\\vert|\\lvert|\\lceil|\\lfloor|\\vert|\\lvert|\\langle|\\llcorner|\\ulcorner)")
r_right = re.compile(r"\\m?right(\\\}|\}|\\\||\||\]|\)|\\rbrack|\\rgroup|\\rbrace|\\rbrack|\\vert|\\rvert|\\rceil|\\rfloor|\\vert|\\rvert|\\rangle|\\lrcorner|\\urcorner)")

empty_text_regex = re.compile(r"\\text\s*\{\s*\}")

# Units regex
units = [
    "integer" "point",
    "feet",
    "sue",
    "digit",
    "pound",
    "meal",
    "edge",
    "student",
    "children ticket",
    "multiple",
    "east",
    "degree",
    "mph",
    "kmph",
    "ft",
    "m square",
    " m east",
    "sq m",
    "deg",
    "mile",
    "q .",
    "monkey",
    "prime",
    "ratio",
    "profit of rs",
    "rd",
    "o",
    "gm",
    "p . m",
    "lb",
    "tile",
    "per",
    "dm",
    "lt",
    "gain",
    "ab",
    "way",
    "west",
    "a .",
    "b .",
    "c .",
    "d .",
    "e .",
    "f .",
    "g .",
    "h .",
    "t",
    "h",
    "no change",
    "men",
    "soldier",
    "pie",
    "bc",
    "excess",
    "st",
    "inches",
    "noon",
    "cent",
    "by",
    "gal",
    "kmh",
    "c",
    "acre",
    "rise",
    "a . m",
    "th",
    "π r 2",
    "sq",
    "mark",
    "l",
    "toy",
    "coin",
    "sq . m",
    "gallon",
    "° f",
    "profit",
    "minw",
    "yr",
    "women",
    "am",
    "pm",
    "hr",
    "cu cm",
    "square",
    "v â € ™",
    "are",
    "rupee",
    "rounds",
    "cubic",
    "cc",
    "mtr",
    "s",
    "ohm",
    "number",
    "kmph",
    "day",
    "hour",
    "minute",
    "min",
    "second",
    "man",
    "woman",
    "sec",
    "cube",
    "mt",
    "sq inch",
    "mp",
    "∏ cm ³",
    "hectare",
    "more",
    "sec",
    "unit",
    "cu . m",
    "cm 2",
    "rs .",
    "rs",
    "kg",
    "g",
    "month",
    "km",
    "m",
    "cm",
    "mm",
    "apple",
    "liter",
    "loss",
    "yard",
    "pure",
    "year",
    "increase",
    "decrease",
    "d",
    "less",
    "Surface",
    "litre",
    "pi sq m",
    "s .",
    "metre",
    "meter",
    "inch",
]

# We sort here to that when matching from right the longest units are matched first
# E.g "percent" is matched before "cent"

units_regex = re.compile("|".join([f"(?=\\s)(?:{unit}(?:s|es)?)($|\\W)" for unit in units]))

# Basic latex regex
to_remove_regex = re.compile(
    r"\\mathrm\{th\}|"  # "th"
    r"\\!\s*|"  # comma with inverse space
    r"\\text\s*\{\s*\}|" # text with empty braces
    r"\\\$|\$|"  # dollar signs
    r"(?<!\\)[\"\']|"  # quotes
    # to display
    r"\\displaystyle"
)

# Text replacement patterns
to_replace_patterns = [
    # (name, pattern, replacement)
    # Not really needed only for units
    ("math", r"\\math(?:rm|it|bf)", r"\text"),
    ("text", r"\\text(?:normal|bf|it|rm)", r"\text"),
    ("frac", r"\\(?:d|t|c)frac", r"\frac"),
    ("decimal_space", r"\s\.", r" 0."),
    ("decimal_brace", r"\{\.", r"{0."),
    ("approx", r"\~\=", r"\approx"),
    ("comma", r"\s*\{\s*,\s*\}", r","),
    ("and", r"(?<=\s)(and)(?=\s)", r" "),
    ("backslash_space", r"(?<!\\)\\\s", r" "),
    # Empty text
    ("infinity", r"infinity", r"\infty"),
    # Dots
    ("dot", r",?(\\ldots)", r" "),
    ("percent", r"\s*percent", r"\\%"),
    ("percent_in_text", r"\\text{percent}", r"\\%"),
    ("inf", r"((?<!\\)inf(?!inity))", r"\infty"),
    ("sqrt", r" sqrt", r"\sqrt"),
]

# Create regex with named groups
pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern, _ in to_replace_patterns)
to_replace_regex = re.compile(pattern)

# Create lookup dictionary for replacements
replacements = {name: replacement for name, _, replacement in to_replace_patterns}

command_slash_fix_regex = re.compile(r"\\\\(?=[a-zA-Z])")
permutation_regex = re.compile(r"\(([a-zA-Z0-9+\-*/\\ ]+?)\)_{([a-zA-Z0-9+\-*/\\ ]+?)}")
equation_split_regex = re.compile(r"(?<!\\|\<|\!|\>)=")
unit_superscript_regex = re.compile(r"\\text{.*?}(\^\d|\{\^\d\})?$")
approx_split_regex = re.compile(r"\\approx")

# Malformed operators regex
malformed_operators_patterns = [
    (re.compile(r"\^\s?\((.*?)\)"), r"^{\1}"),
    (re.compile(r"sqrt\s?\((.*?)\)"), r"\\sqrt{\1}"),
    (re.compile(r"\\frac\s?(\d)\s?(\d+)"), r"\\frac{\1}{\2}"),
    (re.compile(r"\\log_\s?(\d)\s?(\d+)"), r"\\log_{\1}{\2}"),
    (re.compile(r"\\frac\s?{(.*?)}\s?(\d)"), r"\\frac{\1}{\2}"),
    (re.compile(r"\\frac\s?(\d)\s?{(.*?)}"), r"\\frac{\1}{\2}"),
    (re.compile(r"\\sqrt\s?(\d)"), r"\\sqrt{\1}")
]

def _fix_malformed_operators(text: str) -> str:
    """Fix malformed operators in the given text."""
    expr_str = text
    for pattern, replacement in malformed_operators_patterns:
        expr_str = pattern.sub(replacement, expr_str)
    expr_str = expr_str.replace(" sqrt", "\\sqrt")
    return expr_str

def replace(match):
    # Find which group matched
    # Get corresponding replacement from dict
    return replacements[match.lastgroup]

def replace_in_latex(text: str) -> str:
    return to_replace_regex.sub(replace, text)

def extract_last_boxed_content(text: str) -> str:
    """
    Find and extract the content of the last \\boxed{...} or \\fbox{...} element from a string.

    Example:
    >>> extract_last_boxed_content("Some text \\boxed{\\frac{2}{3}}")
    "\\frac{2}{3}"
    >>> extract_last_boxed_content("\\boxed 123")
    "123"
    >>> extract_last_boxed_content("No box here")
    ""
    """

    # Then look for \\boxed{...} or \\fbox{...}
    env = "\\boxed"
    left_idx = text.rfind(env)
    if left_idx < 0:
        env = "\\fbox"
        left_idx = text.rfind(env)
        if left_idx < 0:
            return text
    left_idx += len(env)

    # If the next character is a brace remove it, otherwise it's a \\boxed {content}
    if len(text) > left_idx and text[left_idx] not in ["{", "["]:
        # If there is no opening brace, it's a \\boxed {content}
        return text[left_idx:].lstrip()

    # Find matching closing brace
    i = left_idx
    num_left_braces_open = 0
    while i < len(text):
        if text[i] == "{":
            num_left_braces_open += 1
        if text[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                # Extract content between braces (+1 to remove the opening brace)
                return text[left_idx + 1 : i]
        i += 1

    # Otherwise, it's no a valid latex
    return text

def _fix_fracs(text: str) -> str:
    """
    Fix the formatting of fractions in the given text.
    Copied from: https://github.com/hendrycks/math/blob/357963a7f5501a6c1708cf3f3fb0cdf525642761/modeling/math_equivalence.py#L1

    Args:
        text (str): The input text.

    Returns:
        str: The text with properly formatted fractions.

    Examples:
        >>> _fix_fracs("\\frac12")
        "\\frac{1}{2}"
        >>> _fix_fracs("\\frac{3}{4}")
        "\\frac{3}{4}"
        >>> _fix_fracs("\\frac1{2}")
        "\\frac{1}{2}"
    """
    substrs = text.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        for substr in substrs[1:]:
            # This allows use to have \\frac{1}{2} and \\ frac1{2}
            substr = substr.lstrip()
            new_str += "\\frac"
            if len(substr) > 0 and substr[0] == "{":
                new_str += substr

            elif len(substr) < 2:
                return text
            else:
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    text = new_str
    return text

def _fix_a_slash_b(text: str) -> str:
    """Source: https://github.com/hendrycks/math
    Reformat fractions formatted as a/b to \\frac{a}{b}.
    Example:
    >>> _fix_a_slash_b("2/3")
    \frac{2}{3}
    """
    if len(text.split("/")) != 2:
        return text
    a_str = text.split("/")[0]
    b_str = text.split("/")[1]
    try:
        a = int(a_str)
        b = int(b_str)
        assert text == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except Exception:
        return text

def _fix_sqrt(text: str) -> str:
    """Source: https://github.com/hendrycks/math
    Reformat square roots.
    Example:
    >>> _fix_sqrt("\\sqrt3")
    \\sqrt{3}
    """
    if "\\sqrt" not in text:
        return text
    splits = text.split("\\sqrt")
    new_string = splits[0]
    for split in splits[1:]:
        split = split.lstrip()
        if len(split) > 0 and split[0] not in ["{", "["]:
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string

def normalize_latex(text: str, config: NormalizationConfig) -> str:
    """Normalize latex string according to the provided configuration.
    
    Args:
        text: The latex string to normalize
        config: Configuration controlling which normalizations to apply
        
    Returns:
        The normalized latex string
    """
    if config.boxed:
        text = extract_last_boxed_content(text)

    if config.basic_latex:
        # Basic latex command replacements
        text = text.replace(r'\mathrm{T}', 'T')
        text = text.replace(r'\mathrm{d}', 'd').replace(r'{\rm d}', 'd')
        text = text.replace(r'\left[\begin{matrix}', r'\begin{bmatrix}').replace(r'\end{matrix}\right]', r'\end{bmatrix}')
        text = r_left.sub(r'\1', text)
        text = r_right.sub(r'\1', text)
        text = permutation_regex.sub(r"\\frac{(\1)!}{((\1)-(\2))!}", text)
        
        # Remove useless latex commands
        text = to_remove_regex.sub("", text)
        text = replace_in_latex(text)
        
        # Remove new lines and simplify tabs
        text = text.replace("\n", " ").replace("\t", " ")
        
        # Fix doubled backslashes in commands
        if "matrix" not in text:
            text = command_slash_fix_regex.sub(r"\\", text)
    
    if config.equations:
        eq_parts = equation_split_regex.split(text)
        # We only shorten if there are more than 2 parts, otherwise we keep equation as is
        if len(eq_parts) > 2:
            text = eq_parts[-1]
    
    if config.units:
        # Remove the units and possibly the superscript
        _text = unit_superscript_regex.sub("", text).strip()
        if _text != "" and _text != text:
            text = _text
            
        # Remove unit texts
        for _ in range(2):
            _text = units_regex.sub(r"\1\2", text)
            if _text != "" and _text != text:
                text = _text
        
        # This can trigger empty \text{...}
        # Make sure not to remove space this created
        text = empty_text_regex.sub(" ", text)
    
    if config.nits:
        # Fix leading decimal
        if len(text) > 0 and text[0] == ".":
            text = "0" + text
            
        # Fix 0.5 to fraction
        if text == "0.5":
            text = "\\frac{1}{2}"
    
    if config.malformed_operators:
        # Fix malformed operators
        text = _fix_malformed_operators(text)
        text = _fix_sqrt(text)
        text = _fix_fracs(text)
        text = _fix_a_slash_b(text)
    
    return text.strip()