from fastapi import FastAPI, Depends
from apis.dependencies import get_current_user
from database import Base, engine
from apis.tasks import router as task_router
from apis.projects import router as project_router
from apis.users import router as user_router
from apis.sprints import router as sprint_router
from apis.search_bar import router as search_router
from apis.comments import router as comment_scetion
from fastapi.middleware.cors import CORSMiddleware
from apis.ai import router as ai_router
from apis.ai import router as ai_router
from apis.auth import router as auth_router
from apis.organizations import router as organization_router


from dotenv import load_dotenv
load_dotenv()






app = FastAPI(
    title="Sprint Manager API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "https://sprintmangerui.vercel.app" , "http://localhost:3000", "*" ],  # React / Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create PostgreSQL tables
Base.metadata.create_all(bind=engine)


# Include API Routes
# Protected Routes (Require Token)
app.include_router(task_router, prefix="/tasks", tags=["Tasks"], dependencies=[Depends(get_current_user)])
app.include_router(project_router, prefix="/projects", tags=["Projects"], dependencies=[Depends(get_current_user)])
app.include_router(sprint_router, prefix="/sprints", tags=["Sprints"], dependencies=[Depends(get_current_user)])
app.include_router(ai_router,prefix="/ai",tags=["Ai"], dependencies=[Depends(get_current_user)])
app.include_router(search_router,prefix="/search_bar",tags=["Search"], dependencies=[Depends(get_current_user)])
app.include_router(comment_scetion,prefix="/comment_scetion",tags=["comment_section"], dependencies=[Depends(get_current_user)])
app.include_router(organization_router, prefix="/organizations", tags=["Organizations"], dependencies=[Depends(get_current_user)])

# Public / Semi-Public Routes
app.include_router(user_router, prefix="/users", tags=["Users"]) # Users has mixed public/protected routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
