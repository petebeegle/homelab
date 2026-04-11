#!/usr/bin/env bash
# PreCompact: auto
#
# Fires when Claude Code auto-compacts the conversation (context ~50% full).
# Emits a system message so you're aware compaction happened mid-session.
# If you're mid-implementation, consider /clear + fresh context instead of
# continuing through the summary — summaries lose nuance on complex tasks.
#
# matcher:"auto" in settings.json means this only fires for auto-compact,
# not manual /compact (which is intentional and needs no warning).

echo '{"systemMessage":"Auto-compact fired — context was getting full. If mid-implementation, consider /clear + restate the task with fresh context. Manual /compact at logical boundaries (after research, after milestones) is preferred over auto-compact mid-task."}'
