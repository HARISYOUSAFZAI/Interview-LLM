prompt_template = """
You are an expert at creating questions based on coding materials and documentation.
Your goral is to prepate a coder or programmer for their exam and coding tests.
You do this by asking questions about the text below:

--------------------------------
{text}
--------------------------------

create questions that will prepare the coder or programmer for their exam and coding tests.
Mske sure not to lose any important information from the text.

QUESTIONS:
"""
refine_template = ("""
You are an expert at creating questions based on coding materials and documentation.
Your goal is to help a coder or programmer prepare for their exam and coding tests.
We have received some practice questions to a certain extent: {existing_answer}.
(only if necessary) with some more contect below.

--------------------------------
{text}
--------------------------------
                   
Given the new contect, refine the original question in English.
If the context is not helpful, please provide the original question.
QUESTION:
""")