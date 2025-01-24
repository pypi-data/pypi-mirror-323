from enum import Enum



class UserRole(Enum):
    SYSTEM_ROLE = "system"
    USER_ROLE = "user"

class AgentType(Enum):
    DICTIONARY_AGENT = "dictionary"
    TRANSLATOR_AGENT = "translator"
    
class AIModel(Enum):
    LLAMA_3_70B_VERSATILE = "llama-3.1-70b-versatile"
    LLAMA_3_1_NEMOTRON_70B_INSTRUCT = "nvidia/llama-3.1-nemotron-70b-instruct"


DOCUMENTATION_RULES = """
Clarity and Simplicity: Documentation should avoid jargon and complex language, focusing instead on clear, concise explanations that cater to the target audience's level of expertise. Plain language, simple examples, and a focus on practical information are essential.

Comprehensive Coverage: A good documentation set covers all aspects of the codebase—overview, setup, dependencies, code structure, APIs, and usage examples—without overwhelming the reader with excessive detail. Comprehensive coverage also includes documenting edge cases, limitations, and known issues.

Organization and Structure: Documentation should be logically structured, making it easy for users to find information. Using a table of contents, consistent headers, and grouping related topics together allows readers to locate information quickly.

Up-to-Date Information: Good documentation is current with the latest version of the codebase. Outdated documentation can be worse than none, as it misleads users. Regular updates and clear versioning can help users understand changes over time.

Example-Rich Content: Real-world examples, code snippets, and use cases help users understand how to use functions, classes, and modules. Examples also provide a testing ground for users to understand specific functionality before using it in their code.

Clear API Documentation: For codebases with extensive API interactions, documenting each endpoint or function with parameters, return types, expected inputs, and outputs is essential. Any peculiarities or non-standard behaviors should also be clearly noted.

Error and Debugging Guidance: Good documentation doesn’t just show what works; it also helps when things go wrong. Including common errors, debugging tips, and troubleshooting sections can save users considerable time.

Searchable and Accessible: Whether it’s a single README file or a full documentation site, users should be able to quickly search for and navigate to the relevant information.

Consistent Style and Formatting: A consistent tone, style, and formatting across documentation help readers follow along without distraction. Using code blocks, bullet points, tables, and diagrams where appropriate enhances readability.

Assumptions and Prerequisites: Clarify any assumptions about the user’s environment or knowledge level. Noting prerequisites (e.g., necessary libraries, hardware requirements) allows users to prepare accordingly, minimizing setup issues.

Maintenance Tips and Code Style: Including code conventions, architecture guidelines, and naming conventions makes it easier for other developers to follow best practices and contribute effectively.

Open to Contributions: For open-source projects, guidelines on how to contribute to the codebase, submit issues, or suggest documentation changes can foster a stronger development community and improve the quality of the documentation over time.
"""



COMMANDS: dict[str, str] = {
        "w_test_py": """
        you are a senior developer with 40 years of experience in professional programiming and software testing.
        Generate unit tests for each function, class and method in the this file. Include test cases for various edge cases, typical cases, and error-handling scenarios.
        Create unit tests in Python using the unittest module for the classes and functions in this file. Write each test case with clear assertions and explain any mocks or setup required.
        Write pytest-compatible tests for all functions and classes in this file. Focus on testing input validation, edge cases, and typical use cases for each function.
        When writing unit tests for the classes in this file. Ensure coverage for all methods, including initialization, helper methods, and public methods. Test different input scenarios and edge cases.
        Include setup and teardown steps if needed, and make sure to test edge cases and expected exceptions.
        Make use of mocks where external resources (like databases or APIs) are involved.
        Include examples of inputs that should pass, fail, or raise specific exceptions.
        focusing on different types of input validation, boundary conditions, and return values.
        For functions and classes that depend on external resources, such as databases or APIs, generate unit tests using mocks or stubs to isolate functionality.
        Include scenarios where errors should be raised. Verify that appropriate error messages are provided and correct exceptions are raised.
        """,
        "w_code": "you are a helpful assistant that acts as a translator with 30 years of experience and that cares about the nuances and jargon of the languages he operate with.",
        "w_doc": f"""You are a senior developer with 40 years of experience in professional programiming. Write a profecional looking documentation for this code base using markdown conventions and your response should only limit its self to the markdown documentation, no additional text.
        Your response should follow this roules : ${DOCUMENTATION_RULES}
        """
}
