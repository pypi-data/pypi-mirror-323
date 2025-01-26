import typer
from typing_extensions import Annotated
from groq import Groq
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
GROQ_API_KEY = os.getenv('groq_api_key')
client = Groq(api_key=GROQ_API_KEY)

def scrape_cfiles(files):
    r = []
    for file in files:
        with open(file) as f:
            for l in f.readlines():
                if l[:3] == 'def':
                    r.append(l[4:l.find('(')])
    
    return r

def lucidate(
        comp: Annotated[str, typer.Argument(help="The keyword for the language you are invoking, ex) python3 or Rscript.")],
        file: Annotated[str, typer.Argument(help="The name of the file you are executing - in the same directory or the full path, ex) test.js or homework.cpp")],
        consider: Annotated[str, typer.Option(help='The files (local or full path) you want to consider contextually - separated by ^&, ex) "test1.py ^& test2.py"')] = "",
        full: Annotated[bool, typer.Option('--full', help='Toggle for displaying the full error message in addition to the Lucidated version.')] = False
):
    ex = comp + ' ' + file

    if not os.path.exists(file):
        typer.secho("An error occurred.", fg = typer.colors.BRIGHT_RED)
        typer.secho("That file doesn't exist - make sure to be in the right directory or use the full path.")
        return

    files = [file]
    if consider:
        for f in consider.split():
            if f != '^&':
                files.append(f.strip(""))

    sc = scrape_cfiles(files)

    err = subprocess.run(
        ex,
        capture_output=True,
        text=True
    )

    chat_completion = client.chat.completions.create(
        messages = [
            {
                'role' : 'system',
                'content' : 'You are a error message cleaner. Your input will be the output of a piece of code being run. If the input is empty, that means no error occurred, and you should simply state "No error occurred." If the input is not empty, there is no need to state that no error happened. Please just look through the input and identify the source of the error and explain the error to the user in simple and concise terms. If it makes sense, suggest a solution - if the problem is a complex one. Do not use text highlights such as bolding, and be as concise as possible. Please also consider the following Python function names, sourced from the file run and other files in the project, in your analysis of the error. You do not need to include this information in your response, this is solely for contextual purposes. Only mention them if they are directly relevant to the issue. Here is the list:' + str(sc)
            },
            {
                'role' : 'user',
                'content' : err.stderr
            }
        ],
        model="llama-3.3-70b-versatile"
    )

    result = chat_completion.choices[0].message.content
    if result == 'No error occurred.':
        typer.secho(result, fg=typer.colors.GREEN)
        print(
            '''
               __
            o-''|\_____/)
            \_/|_)     )
                \  __  /
                (_/ (_/    yay!!
            '''
        )
    else:
        if full:
            print(err.stderr)
        typer.secho("An error occurred.", fg = typer.colors.BRIGHT_RED)
        typer.secho(result)