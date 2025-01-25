# AI Kit - Supercharge Your AI IDE ⚡️

AI Kit is the first CLI thats not designed for you. Its designed for your agent.

Designed to integrate with a text editor like Cursor or Windsurf (or any environment with a shell), it extends your agent with search, reasoning, and memory. The goal: make myself obsolete. So I can go do other, better, stuff - like scrolling TikTok.

## Only one command for you
This creates an `.ai-kit` directory that both you and your agent have control over.

`init`
Initialize or reset AI Kit in your project.
```bash
ai-kit init
```

## Commands For Your Agent
`list`
List all commands available to your agent
```bash
ai-kit list
```

`think`
Automatically route complex requstes to `deepseek-r1`, retuning the though stream back to the execution agent in your editor
```bash
ai-kit think "What does this code do?"
```

`web`
Search the web using DuckDuckGo
```bash
ai-kit web "query"
ai-kit web -n 5 "specific query"
```

`status`
Show the status of your AI Kit
```bash
ai-kit status
```