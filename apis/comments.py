
from fastapi import APIRouter,Depends ,HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from datetime import datetime , timezone
from models.user import User 
from models.task import Task
from models.comment import Comment
from apis.schemas.comments import CommentCreate, CommentOut,CommentBase
from core.auth import get_current_user
from typing import List




router= APIRouter()



#CREATE COMMENT

@router.post("/", response_model=CommentOut)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == comment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_comment = Comment(text=comment.text, user_id=comment.user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment



#GET ALL COMMENTS
@router.get("/", response_model=List[CommentOut])
def get_all_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()




#GET COMMENT BY ID
@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment



# UPDATE COMMENT
@router.put("/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, comment_update: CommentCreate, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment.text = comment_update.text
    db.commit()
    db.refresh(comment)
    return comment




# DELETE COMMENT
@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}



