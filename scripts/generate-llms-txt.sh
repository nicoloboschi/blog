#!/bin/bash
# Generate llms.txt from all published blog posts

set -e

OUTPUT_FILE="public/llms.txt"

# Header
cat > "$OUTPUT_FILE" << 'EOF'
# Nicolò Boschi's Blog

> Software Engineer. Distributed Systems. AI Agents. Open Source.

Website: https://nicoloboschi.com
Author: Nicolò Boschi

This file contains all published blog posts for LLM consumption.

---

EOF

# Process each markdown file
for file in content/posts/*.md; do
    # Check if file is a draft
    if grep -q "^draft = true" "$file" 2>/dev/null; then
        continue
    fi

    # Extract title and date using awk
    title=$(awk -F"'" '/^title =/ {print $2; exit}' "$file")
    date=$(awk -F"'" '/^date =/ {print $2; exit}' "$file" | cut -c1-10)

    echo "# $title" >> "$OUTPUT_FILE"
    echo "Date: $date" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # Extract content after frontmatter (delimited by +++)
    awk '
        BEGIN { in_frontmatter = 0; seen_start = 0 }
        /^\+\+\+$/ {
            if (!seen_start) {
                seen_start = 1
                in_frontmatter = 1
                next
            } else {
                in_frontmatter = 0
                next
            }
        }
        !in_frontmatter && seen_start { print }
    ' "$file" >> "$OUTPUT_FILE"

    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

# Count posts and words
posts=$(grep -c "^# " "$OUTPUT_FILE" || echo 0)
words=$(wc -w < "$OUTPUT_FILE" | tr -d ' ')
lines=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')

echo "Generated $OUTPUT_FILE"
echo "  Posts: $posts"
echo "  Words: $words"
echo "  Lines: $lines"
