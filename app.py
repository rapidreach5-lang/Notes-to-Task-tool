import os
import streamlit as st
from dotenv import load_dotenv
from checklist_service import ChecklistBotService
from schemas import TaskPlanOutput

load_dotenv()

st.set_page_config(page_title="Notes-to-Tasks Checklist Bot", page_icon="✅", layout="wide")
st.title("✅ Notes-to-Tasks Checklist Bot")
st.caption("Μετατροπή σημειώσεων σε διαδραστικό checklist με Gemini API & Pydantic")

default_key = os.getenv("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key", value=default_key, type="password")
model_name = st.sidebar.text_input("Gemini Model", value="gemini-3.5-flash")


def clear_checklist_state() -> None:
    st.session_state.task_plan = None
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("chk_")]
    for k in keys_to_delete:
        del st.session_state[k]


def build_markdown_export(plan: TaskPlanOutput) -> str:
    lines: list[str] = [
        "# Checklist Plan",
        "",
        f"**Σύνοψη:** {plan.summary}",
        "",
    ]
    for t_idx, task in enumerate(plan.tasks):
        lines.append(f"## {task.title}")
        lines.append(f"- **Προτεραιότητα:** `{task.priority}` | **Εκτιμώμενος χρόνος:** `{task.estimated_minutes} λεπτά`")
        lines.append("")
        for c_idx, item in enumerate(task.checklist):
            chk_key = f"chk_{t_idx}_{c_idx}"
            is_done = bool(st.session_state.get(chk_key, item.done))
            mark = "x" if is_done else " "
            lines.append(f"- [{mark}] {item.step}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


notes = st.text_area(
    "Πέτα εδώ τις χύμα σημειώσεις ή εκκρεμότητές σου:",
    height=160,
    placeholder="π.χ. Να στείλω το email στον πελάτη, να ελέγξω το bug στο login και να πάρω καφέ...",
)

if "task_plan" not in st.session_state:
    st.session_state.task_plan = None

col_btn1, col_btn2 = st.columns([2, 1])
with col_btn1:
    convert_clicked = st.button("⚡ Μετατροπή σε Checklist", type="primary")
with col_btn2:
    st.button("🧹 Καθαρισμός / Reset", on_click=clear_checklist_state)

if convert_clicked:
    if not api_key.strip():
        st.error("Βάλε πρώτα το Gemini API Key στο .env ή στην αριστερή μπάρα.")
    elif not notes.strip():
        st.warning("Γράψε ή επικόλλησε πρώτα μερικές σημειώσεις.")
    else:
        try:
            clear_checklist_state()
            service = ChecklistBotService(api_key=api_key.strip(), model=model_name.strip())
            with st.spinner("Οργανώνω τις σημειώσεις σου σε checklist..."):
                st.session_state.task_plan = service.notes_to_tasks(notes)
        except Exception as e:
            st.error(f"Σφάλμα κατά την κλήση του Gemini API: {e}")

plan = st.session_state.task_plan
if plan:
    st.markdown("---")
    st.subheader("📋 Σύνοψη Πλάνου")
    st.info(plan.summary)

    total_steps = sum(len(t.checklist) for t in plan.tasks)
    checked_steps = 0

    for t_idx, task in enumerate(plan.tasks):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {task.title}")
            with col2:
                st.markdown(f"**Προτεραιότητα:** `{task.priority}` · ⏱️ `{task.estimated_minutes} λεπτά`")

            for c_idx, item in enumerate(task.checklist):
                key = f"chk_{t_idx}_{c_idx}"
                is_checked = st.checkbox(item.step, value=item.done, key=key)
                if is_checked:
                    checked_steps += 1

    if total_steps > 0:
        progress = checked_steps / total_steps
        st.markdown("### 📊 Πρόοδος Checklist")
        st.progress(progress, text=f"{checked_steps} / {total_steps} βήματα ολοκληρωμένα ({int(progress * 100)}%)")

    md_content = build_markdown_export(plan)
    st.download_button(
        label="⬇️ Λήψη Checklist σε Markdown (.md)",
        data=md_content,
        file_name="checklist_plan.md",
        mime="text/markdown",
    )