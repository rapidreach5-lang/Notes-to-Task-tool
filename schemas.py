from typing import List, Literal
from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    step: str = Field(..., description="Συγκεκριμένο, εκτελέσιμο βήμα του checklist")
    done: bool = Field(default=False, description="Αν έχει ολοκληρωθεί")


class TaskCard(BaseModel):
    title: str = Field(..., description="Σύντομος και ξεκάθαρος τίτλος εργασίας")
    priority: Literal["Low", "Medium", "High"] = Field(..., description="Βαθμός προτεραιότητας")
    estimated_minutes: int = Field(..., ge=1, description="Εκτιμώμενος χρόνος σε λεπτά")
    checklist: List[ChecklistItem] = Field(..., description="Λίστα βημάτων για τσεκάρισμα")


class TaskPlanOutput(BaseModel):
    summary: str = Field(..., description="Μία πρόταση που συνοψίζει τι αφορά το πλάνο")
    tasks: List[TaskCard] = Field(..., description="Τα tasks που προκύπτουν από τις σημειώσεις")