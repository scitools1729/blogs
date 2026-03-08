- To count the number of lines in a CSV form command line:
```bash
python -c "import csv; print(sum(1 for row in csv.reader(open('redcode_prompts.csv', encoding='utf-8'))))"
```

- to tar a directory with just the source files and related files
```bash
find core-llmesh \
  -name "__pycache__" -prune -o \
  -name "outputs" -prune -o \
  -type d -print -o \
  \( -name "*.py" -o -name "*.yaml" -o -name "*.toml" -o -name "*.md" \) -print \
  | tar -cvzf corellmesh.tar.gz --no-recursion -T -
```
