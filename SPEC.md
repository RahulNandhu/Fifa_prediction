# FIFA World Cup Prediction Contest Application - Development Plan

## Project Goal

Develop a company-only FIFA World Cup Prediction Contest web application using Django. The application will allow approved users to predict match outcomes and compete on leaderboards while administrators manage contests, members, matches, and scoring through Django's built-in Admin Panel.

---

# Technology Stack

## Backend & Frontend

* Django (Full Stack Framework)
* Django Templates
* Bootstrap 5
* PostgreSQL

## Authentication

* Django Built-in Authentication

## Hosting

* Django Application: Render or Railway
* PostgreSQL: Neon or Render PostgreSQL

---

# Architecture

## User-Facing Application

Custom Django pages for:

* Login
* Registration
* Dashboard
* Upcoming Matches
* Prediction Submission
* My Predictions
* Overall Leaderboard
* Weekly Leaderboard
* Group Join Requests

## Admin Interface

Use Django Admin for:

* User Management
* Group Management
* Membership Approvals
* Match Publishing
* Match Result Entry
* Point Adjustments
* Prediction Monitoring

No custom admin dashboard will be developed in Version 1.

---

# User Roles

## Admin

Responsibilities:

* Create contest groups
* Approve or reject membership requests
* Publish matches
* Enter actual results
* Adjust user points
* View predictions
* Manage users

Admins will access:

/admin

through Django Admin.

## User

Capabilities:

* Register
* Login
* Request group access
* Submit predictions
* View leaderboards
* View personal prediction history

---

# Contest Group Flow

## Group Creation

Admin creates:

Example:

Analystor FIFA World Cup 2026

## Membership Request

User Flow:

1. Register
2. Login
3. View available groups
4. Request to join
5. Await approval

## Approval

Admin Flow:

1. Open Django Admin
2. Review membership requests
3. Approve or reject

Only approved members can participate.

---

# Match Management

## Fixture Source

World Cup fixtures will be maintained as seed data.

Recommended approach:

fixtures.json

containing:

* Fixture ID
* Home Team
* Away Team
* Kickoff Date & Time

## Upcoming Fixtures

Admin can view all seeded fixtures in Django Admin.

## Publish Match

Admin clicks:

Published = True

Once published:

* Match becomes visible to users
* Prediction deadline is generated

Only published matches appear in user dashboards.

---

# Prediction Deadline

Rule:

Prediction Deadline = Kickoff Time

Examples:

Kickoff:
20:00

Prediction Closes:
20:00

Rules:

* Users can create predictions before deadline.
* Users can edit predictions before deadline.
* Predictions are locked after deadline.
* Backend validation is mandatory.

---

# Prediction System

Users can submit:

## Winner Prediction

Options:

* Home Team
* Away Team
* Draw

## Scoreline Prediction

Examples:

* Brazil 2 - 1 Germany
* Brazil 1 - 1 Germany

Users can modify predictions until the deadline.

---

# Prediction Visibility Rules

## Before Deadline

Users cannot view other users' predictions.

Display:

Predictions Submitted: 24

## After Deadline

Display statistics:

Brazil Win: 70%
Draw: 20%
Germany Win: 10%

This prevents copying.

---

# Match Result Processing

After a match concludes:

Admin enters:

Home Score
Away Score

The system automatically:

1. Calculates points
2. Updates predictions
3. Updates leaderboards

---

# Points System

Winner Prediction Correct:
2 Points

Exact Scoreline Correct:
2 Points

Both Correct Bonus:
1 Point

Maximum per match:
5 Points

Examples:

Winner Correct Only:
2 Points

Winner + Exact Score:
5 Points (2 + 2 + 1 bonus)

Incorrect Prediction:
0 Points

---

# Leaderboards

## Overall Leaderboard

Ranks users by total points accumulated throughout the tournament.

## Weekly Leaderboard

Ranks users based on points earned during a specific week.

---

# Manual Point Adjustments

Admins can:

* Add points
* Deduct points

Reasons:

* System correction
* Bonus points
* Administrative adjustment

Every adjustment must be logged.

---

# Audit Logging

Store:

* User
* Point Change
* Reason
* Timestamp
* Admin User

This provides a complete audit trail.

---

# Database Models

## User

Use Django's built-in User model.

## ContestGroup

Stores contest information.

## GroupMembership

Stores:

* User
* Group
* Status

Statuses:

* Pending
* Approved
* Rejected

## Fixture

Stores seeded World Cup fixture data.

## Match

Stores published matches.

## Prediction

Stores user predictions.

## PointTransaction

Stores manual adjustments and audit history.

---

# Django Admin Usage

Use Django Admin for:

## User Management

* Activate users
* Deactivate users

## Group Management

* Create groups
* Edit groups

## Membership Requests

* Approve requests
* Reject requests

## Match Publishing

* Publish matches

## Result Entry

* Enter actual scores

## Point Adjustments

* Add or deduct points

## Prediction Monitoring

* View all predictions

---

# UI Pages

## Authentication

* Login
* Register

## User Dashboard

Displays:

* Upcoming Matches
* Prediction Status
* Group Membership Status
* Leaderboard Summary

## Match Prediction Page

Allows users to:

* Predict winner
* Predict scoreline
* Update prediction before deadline

## My Predictions

Displays all submitted predictions.

## Overall Leaderboard

Displays tournament rankings.

## Weekly Leaderboard

Displays weekly rankings.

## Group Request Page

Displays:

* Available Groups
* Join Requests
* Approval Status

---

# Initial Admin Setup

After deployment:

1. Run migrations

2. Create first administrator:

python manage.py createsuperuser

3. Login to:

https://your-domain.com/admin

4. Create contest group

5. Import fixture data

6. Publish matches

7. Start accepting user registrations

---

# Development Phases

## Phase 1 - Project Setup

* Setup Django project
* Configure PostgreSQL
* Configure Bootstrap
* Configure Authentication
* Configure Django Admin

Estimated Time:
1 Day

---

## Phase 2 - Core Models

* ContestGroup
* GroupMembership
* Fixture
* Match
* Prediction
* PointTransaction

Estimated Time:
1 Day

---

## Phase 3 - User Features

* Registration
* Login
* Dashboard
* Join Group Request

Estimated Time:
1-2 Days

---

## Phase 4 - Prediction System

* Publish Match Logic
* Prediction Submission
* Prediction Deadline Validation
* Prediction Editing

Estimated Time:
1-2 Days

---

## Phase 5 - Scoring & Leaderboards

* Automatic Point Calculation
* Overall Leaderboard
* Weekly Leaderboard

Estimated Time:
1 Day

---

## Phase 6 - Admin Operations

* Membership Approval Workflow
* Result Entry
* Point Adjustments
* Audit Logging

Estimated Time:
1 Day

---

## Phase 7 - Deployment

* Deploy Django App
* Configure PostgreSQL
* Configure Static Files
* Create Superuser
* Production Testing

Estimated Time:
1 Day

---

# MVP Success Criteria

The application is considered complete when:

* Users can register and login.
* Users can request group access.
* Admins can approve members.
* Admins can publish World Cup matches.
* Users can predict winners and scorelines.
* Prediction deadlines are enforced.
* Results can be entered by admins.
* Points are calculated automatically.
* Overall and weekly leaderboards are available.
* Admins can manually adjust points.
* All administrative actions are auditable.
* The application is deployed and accessible online.
