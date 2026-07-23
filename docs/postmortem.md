# Postmortem: Cross-Mode Session-State Leakage in Streamlit

## Summary

During Week 2 and Week 3, I encountered a bug where switching between application modes caused unexpected behavior. Chat history, document paths, or workspace state from one mode could appear in another mode. This was caused by using shared Streamlit session-state keys across multiple modes.

---

## Symptoms

The app showed several confusing behaviors:

- Chat messages from Chat mode appeared after switching to another mode.
- Document paths from one workspace were sometimes reused incorrectly.
- Resetting one workspace affected another workspace.
- The UI state did not feel isolated between Chat, Compare, Quiz, and Eval modes.

---

## Root Cause

Streamlit reruns the entire script on every interaction. Persistent UI state must be stored in `st.session_state`.

Initially, I used shared state patterns without fully isolating each mode. Because Chat, Compare, Quiz, and Eval all used the same application script, switching modes could cause state contamination.

The core issue was that mode-specific data was not namespaced properly.

---

## Fix

I redesigned the session-state architecture so that each mode has its own isolated state dictionary.

Examples:

```python
st.session_state["chat_paths"]
st.session_state["compare_paths"]
st.session_state["quiz_paths"]
st.session_state["eval_paths"]
```

Each mode also has its own message or data state:

```python
st.session_state.chat_messages
st.session_state.compare_messages
st.session_state.quiz_data
st.session_state.quiz_submitted
st.session_state.user_answers
```

The Reset Workspace button was updated to clear only the active mode’s state, not all state.

---

## Lessons Learned

1. Streamlit’s simplicity can hide state-management complexity.
2. Multi-mode apps need explicit namespacing.
3. Bugs caused by shared state are often confusing because they appear in unrelated parts of the UI.
4. Reset actions should be scoped carefully.
5. This issue directly led to ADR-003, which documents the isolated workspace decision.

---

## Impact

After the fix:

- Each mode behaves like an independent workspace.
- Switching modes no longer contaminates chat history or document paths.
- Resetting one mode does not destroy another mode’s state.
- The application became easier to extend with new modes.
```
