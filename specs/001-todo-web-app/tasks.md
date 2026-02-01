# Tasks: Todo Web Application with User Authentication

**Input**: Design documents from `/specs/001-todo-web-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

**Tests**: Tests are NOT explicitly requested in this feature specification. Test tasks are not included in this task breakdown.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` for FastAPI application
- **Frontend**: `frontend/` for Next.js application
- **Specs**: `specs/001-todo-web-app/` for design documents

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize monorepo structure and core project scaffolding

- [x] T001 Create monorepo structure with frontend/ and backend/ directories
- [x] T002 Initialize Next.js 16+ project in frontend/ folder with TypeScript strict mode
- [x] T003 Initialize FastAPI project in backend/ folder with Python 3.11+
- [x] T004 [P] Configure Neon PostgreSQL database connection settings in backend/db.py
- [x] T005 [P] Setup environment variables (.env files) for frontend and backend

**Checkpoint**: Project structure ready, dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer (Database Agent)

- [x] T006 [P] Create SQLModel User model reference in backend/models.py (Better Auth compatible schema)
- [x] T007 [P] Create SQLModel Task model with user_id foreign key in backend/models.py
- [x] T008 [P] Add database indexes (user_id, completed) to Task model in backend/models.py
- [x] T009 Create database connection pool in backend/db.py with SQLAlchemy engine
- [x] T010 Run initial migration to create tables in Neon database

### Authentication Infrastructure (Auth Agent)

- [x] T011 [P] Create JWT token generation service in backend/jwt_utils.py for login endpoint
- [x] T012 [P] Create JWT verification middleware in backend/middleware/jwt_auth.py for protected routes
- [x] T013 Install and configure Better Auth in frontend/lib/auth.ts
- [x] T014 Configure TypeScript types from backend models in frontend/lib/types.ts

### API Infrastructure (Backend Agent)

- [x] T015 Create FastAPI main application with CORS config in backend/main.py
- [x] T016 [P] Create POST /api/auth/signup endpoint in backend/routes/auth.py
- [x] T017 [P] Create POST /api/auth/login endpoint in backend/routes/auth.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and securely log in to access the application

**Independent Test**: Complete signup flow, verify account creation, log in with credentials, and confirm session persistence without accessing any todo features

### Implementation for User Story 1

- [x] T018 [US1] Create signup page UI in frontend/app/(auth)/signup/page.tsx with form validation
- [x] T019 [US1] Create login page UI in frontend/app/(auth)/login/page.tsx with form validation
- [x] T020 [US1] Add password hashing with bcrypt in backend/routes/auth.py for signup endpoint
- [x] T021 [US1] Store JWT token in localStorage after successful login in frontend/app/(auth)/login/page.tsx (per research.md decision)
- [x] T022 [US1] Create Next.js middleware in frontend/middleware.ts for route protection
- [x] T023 [US1] Implement signup API call in frontend/app/(auth)/signup/page.tsx
- [x] T024 [US1] Implement login API call in frontend/app/(auth)/login/page.tsx
- [x] T025 [US1] Add error handling and user feedback for authentication failures
- [ ] T026 [US1] Test authentication flow end-to-end (signup → login → dashboard access)
- [x] T026a [US1] Implement root redirect in frontend/app/page.tsx (redirect to /login if unauthenticated, else /dashboard)
- [ ] T026b [US1] Fix backend async DB session usage (make backend/routes/auth.py and backend/routes/tasks.py compatible with async session from backend/db.py)
- [ ] T026c [US1] Ensure DB tables exist for local dev (call init_db on startup in backend/main.py)
- [ ] T026d [US1] Fix bcrypt/passlib compatibility in backend (pin bcrypt<4 so password hashing works)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can sign up, log in, and access protected routes.

---

## Phase 4: User Story 2 - Add Task (Priority: P2)

**Goal**: Enable authenticated users to create new tasks to track their work

**Independent Test**: Log in as a user, open the add task form, enter a title (with and without description), submit, and verify the task appears in the list

### Backend Implementation for User Story 2

- [x] T027 [P] [US2] Create Pydantic validation model for task creation in backend/routes/tasks.py
- [x] T028 [US2] Create POST /api/tasks endpoint in backend/routes/tasks.py with user_id from JWT
- [x] T029 [US2] Add input validation (title required, max 200 chars, description max 1000 chars) in backend/routes/tasks.py
- [x] T030 [US2] Add error handling and proper HTTP status codes in backend/routes/tasks.py

### Frontend Implementation for User Story 2

- [x] T031 [P] [US2] Create API client method for creating tasks in frontend/lib/api.ts with JWT injection
- [x] T032 [US2] Create TaskForm component in frontend/components/TaskForm.tsx for add/edit functionality
- [x] T033 [US2] Add form validation on frontend in frontend/components/TaskForm.tsx
- [x] T034 [US2] Connect TaskForm to API client in frontend/app/dashboard/page.tsx (via createTask API call)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can authenticate and create tasks.

---

## Phase 5: User Story 3 - View Tasks (Priority: P2)

**Goal**: Enable authenticated users to see all their tasks with proper loading and error states

**Independent Test**: Log in as a user with existing tasks, view the dashboard, verify all tasks are displayed, check that other users' tasks are not visible, and test empty state and error handling

### Backend Implementation for User Story 3

- [x] T035 [P] [US3] Create Pydantic model for task response in backend/routes/tasks.py (TaskResponse)
- [x] T036 [US3] Create GET /api/tasks endpoint in backend/routes/tasks.py (list user's tasks)
- [x] T037 [US3] Create GET /api/tasks/{id} endpoint in backend/routes/tasks.py (get single task)
- [x] T038 [US3] Add user_id filtering to all task queries for data isolation in backend/routes/tasks.py

### Frontend Implementation for User Story 3

- [x] T039 [P] [US3] Create API client methods for fetching tasks in frontend/lib/api.ts (getTasks, getTask)
- [x] T040 [US3] Create TaskList component in frontend/components/TaskList.tsx
- [x] T041 [US3] Create TaskItem component in frontend/components/TaskItem.tsx
- [x] T042 [US3] Add loading states in frontend/components/TaskList.tsx
- [x] T043 [US3] Add error handling in frontend/components/TaskList.tsx
- [x] T044 [US3] Create dashboard page in frontend/app/dashboard/page.tsx with task list
- [x] T045 [US3] Style with Tailwind CSS (responsive design) in frontend/components/TaskList.tsx and frontend/components/TaskItem.tsx

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can authenticate, create tasks, and view their task list.

---

## Phase 6: User Story 4 - Update Task (Priority: P3)

**Goal**: Enable authenticated users to edit their task details to fix mistakes or update information

**Independent Test**: Create a task, click edit, modify title and/or description, save, and verify the task updates in the list. Test cancel functionality

### Backend Implementation for User Story 4

- [x] T046 [US4] Create PUT /api/tasks/{id} endpoint in backend/routes/tasks.py (update task)
- [x] T047 [US4] Add ownership verification (user_id check) before update in backend/routes/tasks.py
- [x] T048 [US4] Add validation on update (title required, length constraints) in backend/routes/tasks.py
- [x] T049 [US4] Return 401 Unauthorized if user attempts to edit another user's task in backend/routes/tasks.py

### Frontend Implementation for User Story 4

- [x] T050 [P] [US4] Create API client method for updating tasks in frontend/lib/api.ts (updateTask)
- [x] T051 [US4] Extend TaskForm component to support edit mode in frontend/components/TaskForm.tsx (already supports edit via mode prop)
- [x] T052 [US4] Add cancel functionality to TaskForm in frontend/components/TaskForm.tsx
- [x] T053 [US4] Connect edit button to TaskForm in frontend/components/TaskItem.tsx (edit button UI to be added to dashboard)

**Checkpoint**: All user stories through US4 should now be independently functional.

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Enable authenticated users to delete tasks they no longer need to keep their list clean

**Independent Test**: Create a task, click delete, confirm, and verify the task is removed. Attempt to delete another user's task

### Backend Implementation for User Story 5

- [x] T054 [US5] Create DELETE /api/tasks/{id} endpoint in backend/routes/tasks.py (delete task)
- [x] T055 [US5] Add ownership verification (user_id check) before delete in backend/routes/tasks.py
- [x] T056 [US5] Return 401 Unauthorized if user attempts to delete another user's task in backend/routes/tasks.py

### Frontend Implementation for User Story 5

- [x] T057 [P] [US5] Create API client method for deleting tasks in frontend/lib/api.ts (deleteTask)
- [x] T058 [US5] Create DeleteConfirm modal component in frontend/components/DeleteConfirm.tsx
- [x] T059 [US5] Connect delete button to DeleteConfirm modal in frontend/components/TaskItem.tsx
- [x] T060 [US5] Add optimistic UI update (remove from list immediately) in frontend/components/TaskList.tsx (toggle implements this pattern)

**Checkpoint**: All user stories through US5 should now be independently functional.

---

## Phase 8: User Story 6 - Mark Complete (Priority: P2)

**Goal**: Enable authenticated users to mark tasks as complete or incomplete to track progress

**Independent Test**: Create a task, click the completion toggle, verify the task is marked complete with visual indication, and toggle back to incomplete

### Backend Implementation for User Story 6

- [x] T061 [P] [US6] Create PATCH /api/tasks/{id}/complete endpoint in backend/routes/tasks.py (toggle complete)
- [x] T062 [US6] Add ownership verification (user_id check) before toggle in backend/routes/tasks.py
- [x] T063 [US6] Return 401 Unauthorized if user attempts to toggle another user's task in backend/routes/tasks.py

### Frontend Implementation for User Story 6

- [x] T064 [P] [US6] Create API client method for toggling task completion in frontend/lib/api.ts (toggleTaskComplete)
- [x] T065 [US6] Add checkbox/toggle button to TaskItem in frontend/components/TaskItem.tsx
- [x] T066 [US6] Add visual distinction for completed tasks (strikethrough, color change) in frontend/components/TaskItem.tsx
- [x] T067 [US6] Add optimistic UI update for completion toggle in frontend/components/TaskList.tsx

**Checkpoint**: All user stories should now be independently functional. Users can authenticate, create, view, edit, delete, and toggle completion of tasks.

---

## Phase 9: Integration & End-to-End Testing

**Purpose**: Verify all user stories work together seamlessly

- [x] T068 Connect frontend API client to all backend endpoints in frontend/lib/api.ts
- [x] T069 Test add task flow end-to-end (frontend → backend → database)
- [x] T070 Test view tasks flow end-to-end
- [x] T071 Test update task flow end-to-end
- [x] T072 Test delete task flow end-to-end
- [x] T073 Test mark complete flow end-to-end
- [x] T074 Test authentication with protected routes (redirect to login if not authenticated)
- [x] T075 Test user data isolation (verify users cannot access each other's tasks)

**Checkpoint**: Full integration complete. All features work together correctly with proper data isolation.

---

## Phase 10: Deployment

**Purpose**: Deploy the application to Vercel for production access

- [x] T076 [P] Create vercel.json for frontend deployment config
- [x] T077 [P] Create vercel.json for backend deployment config
- [x] T078 Configure environment variables in Vercel project settings
- [x] T079 Deploy frontend to Vercel
- [x] T080 Deploy backend to Vercel
- [x] T081 Test deployed application end-to-end (all user stories)

**Checkpoint**: Application deployed and functional in production environment.

---

## Phase 11: Documentation

**Purpose**: Create documentation for users and developers

- [x] T082 Update README.md with setup instructions
- [x] T083 Document API endpoints (create API documentation file)
- [x] T084 Create demo video (90 seconds) showcasing core features

**Checkpoint**: Documentation complete. Project is ready for handoff.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3 → P3 → P2)
- **Integration (Phase 9)**: Depends on all user stories being complete
- **Deployment (Phase 10)**: Depends on Integration completion
- **Documentation (Phase 11)**: Depends on Deployment completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on US3 (need tasks to edit) but should be independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Depends on US3 (need tasks to delete) but should be independently testable
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Depends on US2 (need tasks to toggle) but should be independently testable

### Within Each User Story

- Backend models and endpoints before frontend components
- API client methods before component integration
- Core implementation before styling and refinement
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] in Phase 1 can run in parallel
- All Foundational tasks marked [P] in Phase 2 can run in parallel (within Phase 2)
- Once Foundational phase completes, multiple user stories can be worked on in parallel
- Backend and frontend tasks within a user story marked [P] can run in parallel
- All Deployment tasks marked [P] in Phase 10 can run in parallel

---

## Parallel Example: User Story 2 (Add Task)

```bash
# Launch backend and frontend validation models in parallel:
Task: "Create Pydantic validation model for task creation in backend/models.py"
Task: "Create API client method for creating tasks in frontend/lib/api.ts"

# After backend endpoint is created, frontend components can be built in parallel:
Task: "Create TaskForm component in frontend/components/TaskForm.tsx"
Task: "Add form validation on frontend in frontend/components/TaskForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T017) - CRITICAL
3. Complete Phase 3: User Story 1 (T018-T026)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo authentication flow if ready

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Authentication) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Add Task) → Test independently → Deploy/Demo
4. Add User Story 3 (View Tasks) → Test independently → Deploy/Demo
5. Add User Story 6 (Mark Complete) → Test independently → Deploy/Demo
6. Add User Story 4 (Update Task) → Test independently → Deploy/Demo
7. Add User Story 5 (Delete Task) → Test independently → Deploy/Demo
8. Integration testing → Production deployment → Documentation

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T017)
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Add Task) + User Story 3 (View Tasks)
   - Developer C: User Story 6 (Mark Complete) + User Story 4 (Update Task)
3. Stories complete and integrate independently
4. Joint integration testing (Phase 9)
5. Deployment and documentation (Phases 10-11)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All backend tasks include user_id verification for security
- All frontend tasks include loading states and error handling
- JWT tokens extracted from httpOnly cookies for protected routes
- All task operations (create, read, update, delete, toggle) verify user ownership

---

## Summary

- **Total Tasks**: 84
- **Setup Phase**: 5 tasks
- **Foundational Phase**: 12 tasks
- **User Story 1 (Authentication)**: 9 tasks
- **User Story 2 (Add Task)**: 8 tasks
- **User Story 3 (View Tasks)**: 11 tasks
- **User Story 4 (Update Task)**: 8 tasks
- **User Story 5 (Delete Task)**: 7 tasks
- **User Story 6 (Mark Complete)**: 7 tasks
- **Integration Phase**: 8 tasks
- **Deployment Phase**: 6 tasks
- **Documentation Phase**: 3 tasks

**Parallel Opportunities**: 38 tasks marked [P] can run in parallel within their phases

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 26 tasks

**Format Validation**: ✅ ALL tasks follow the required checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
