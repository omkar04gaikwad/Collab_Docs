# Collaborative Docs Project Plan

## Project Overview
A real-time collaborative document editing platform built with Spring Boot, featuring conflict-free replicated data types (CRDTs) for seamless multi-user editing.

## Technology Stack
- **Backend**: Spring Boot 3.5.5, Java 21
- **Database**: PostgreSQL
- **Caching**: Redis
- **Real-time**: WebSocket
- **Security**: Spring Security + OAuth2
- **Frontend**: (To be implemented)

---

## ✅ COMPLETED TASKS

### Phase 0: Project Setup
- [x] **Project Structure Setup**
  - Created Spring Boot project with Maven configuration
  - Set up proper package structure (config, controller, model, service, repository, security, websocket, crdt, dto)
  - Configured Java 21 and Spring Boot 3.5.5

- [x] **Dependencies Configuration**
  - Spring Boot Web Starter
  - Spring Boot WebSocket
  - Spring Security
  - Spring Data JPA
  - Spring Data Redis
  - PostgreSQL Driver
  - OAuth2 Client
  - File Upload (Commons FileUpload)
  - Image Processing (ImgScalr)
  - Validation & Actuator
  - Testing Dependencies

---

## 🚧 TO BE COMPLETED

### Phase 1: Core Infrastructure
- [ ] **Database Configuration**
  - Configure PostgreSQL connection in application.properties
  - Set up JPA/Hibernate settings
  - Configure Redis connection
  - Database migration scripts

- [ ] **Entity Models**
  - User entity with authentication fields
  - Document entity with metadata
  - DocumentVersion for version control
  - DocumentPermission for access control
  - UserSession for tracking active users
  - DocumentOperation for CRDT operations

- [ ] **Security Configuration**
  - Spring Security configuration class
  - JWT token management
  - OAuth2 integration (Google/GitHub)
  - Password encryption
  - CORS configuration

### Phase 2: Basic Functionality
- [ ] **User Management**
  - User registration API
  - User login/logout API
  - User profile management
  - Password reset functionality
  - Email verification

- [ ] **Document CRUD Operations**
  - Create new document
  - Read document content
  - Update document metadata
  - Delete document
  - Document sharing permissions
  - Document versioning

- [ ] **Repository Layer**
  - UserRepository with custom queries
  - DocumentRepository with search capabilities
  - DocumentVersionRepository
  - DocumentPermissionRepository

### Phase 3: Collaboration Features
- [ ] **CRDT Implementation**
  - Character-based CRDT (LSEQ or RGA)
  - Operation transformation algorithms
  - Conflict resolution mechanisms
  - State synchronization

- [ ] **WebSocket Infrastructure**
  - WebSocket configuration
  - Message handling for real-time updates
  - User presence tracking
  - Room management for documents

- [ ] **Real-time Collaboration**
  - Live cursor tracking
  - Real-time text editing
  - User presence indicators
  - Conflict-free editing
  - Operation broadcasting

### Phase 4: Advanced Features
- [ ] **Document Features**
  - Rich text editing support
  - Image upload and processing
  - Document templates
  - Export functionality (PDF, Word)
  - Document comments and suggestions

- [ ] **User Experience**
  - Document search and filtering
  - Recent documents
  - Document sharing via links
  - Notification system
  - User activity tracking

### Phase 5: Frontend Development
- [ ] **Frontend Setup**
  - Choose frontend framework (React/Vue/Angular)
  - Set up build configuration
  - Create responsive design

- [ ] **Document Editor**
  - Rich text editor integration
  - Real-time collaboration UI
  - User presence indicators
  - Document toolbar and formatting

- [ ] **User Interface**
  - Login/Registration pages
  - Document dashboard
  - User profile management
  - Settings and preferences

### Phase 6: Testing & Deployment
- [ ] **Testing**
  - Unit tests for services and repositories
  - Integration tests for APIs
  - WebSocket testing
  - CRDT algorithm testing
  - End-to-end testing

- [ ] **Deployment**
  - Docker containerization
  - CI/CD pipeline setup
  - Production environment configuration
  - Monitoring and logging
  - Performance optimization

---

## 📊 DATABASE SCHEMA

### Users Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User's unique username |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Encrypted password |
| first_name | VARCHAR(100) | NOT NULL | User's first name |
| last_name | VARCHAR(100) | NOT NULL | User's last name |
| avatar_url | VARCHAR(500) | NULL | Profile picture URL |
| is_email_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| last_login | TIMESTAMP | NULL | Last login time |

### Documents Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique document identifier |
| title | VARCHAR(255) | NOT NULL | Document title |
| content | TEXT | NULL | Document content (JSON for CRDT) |
| owner_id | BIGINT | FOREIGN KEY (users.id) | Document owner |
| is_public | BOOLEAN | DEFAULT FALSE | Public visibility |
| is_archived | BOOLEAN | DEFAULT FALSE | Archive status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| last_modified_by | BIGINT | FOREIGN KEY (users.id) | Last editor |

### Document_Versions Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Version identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id) | Parent document |
| version_number | INTEGER | NOT NULL | Version number |
| content_snapshot | TEXT | NOT NULL | Content at this version |
| change_summary | VARCHAR(500) | NULL | Description of changes |
| created_by | BIGINT | FOREIGN KEY (users.id) | Version creator |
| created_at | TIMESTAMP | DEFAULT NOW() | Version creation time |

### Document_Permissions Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Permission identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id) | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id) | User with permission |
| permission_type | VARCHAR(20) | NOT NULL | READ, WRITE, ADMIN |
| granted_by | BIGINT | FOREIGN KEY (users.id) | Permission granter |
| granted_at | TIMESTAMP | DEFAULT NOW() | Permission grant time |
| expires_at | TIMESTAMP | NULL | Permission expiration |

### Document_Operations Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Operation identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id) | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id) | Operation author |
| operation_type | VARCHAR(20) | NOT NULL | INSERT, DELETE, RETAIN |
| position | INTEGER | NOT NULL | Character position |
| content | TEXT | NULL | Content to insert/delete |
| operation_id | VARCHAR(100) | UNIQUE | CRDT operation ID |
| timestamp | BIGINT | NOT NULL | Logical timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Operation creation time |

### User_Sessions Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Session identifier |
| user_id | BIGINT | FOREIGN KEY (users.id) | Session owner |
| session_token | VARCHAR(500) | UNIQUE, NOT NULL | JWT token |
| device_info | VARCHAR(255) | NULL | Device/browser info |
| ip_address | INET | NULL | Client IP address |
| is_active | BOOLEAN | DEFAULT TRUE | Session status |
| created_at | TIMESTAMP | DEFAULT NOW() | Session start time |
| expires_at | TIMESTAMP | NOT NULL | Session expiration |
| last_activity | TIMESTAMP | DEFAULT NOW() | Last activity time |

### Document_Collaborators Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Collaboration identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id) | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id) | Collaborator |
| cursor_position | INTEGER | NULL | Current cursor position |
| selection_start | INTEGER | NULL | Selection start position |
| selection_end | INTEGER | NULL | Selection end position |
| is_online | BOOLEAN | DEFAULT FALSE | Online status |
| last_seen | TIMESTAMP | DEFAULT NOW() | Last activity time |
| joined_at | TIMESTAMP | DEFAULT NOW() | Collaboration start time |

### Document_Comments Table
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Comment identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id) | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id) | Comment author |
| content | TEXT | NOT NULL | Comment text |
| position | INTEGER | NULL | Character position |
| is_resolved | BOOLEAN | DEFAULT FALSE | Resolution status |
| created_at | TIMESTAMP | DEFAULT NOW() | Comment creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

---

## 🎯 MILESTONES

### Milestone 1: Basic Platform (Weeks 1-2)
- Database setup and entity models
- User authentication and authorization
- Basic document CRUD operations

### Milestone 2: Real-time Foundation (Weeks 3-4)
- WebSocket infrastructure
- CRDT implementation
- Basic real-time editing

### Milestone 3: Collaboration Features (Weeks 5-6)
- Live cursor tracking
- User presence
- Conflict resolution

### Milestone 4: Advanced Features (Weeks 7-8)
- Rich text editing
- Comments and suggestions
- Document sharing

### Milestone 5: Frontend & Polish (Weeks 9-10)
- Complete frontend interface
- Testing and optimization
- Deployment preparation

---

## 📈 SUCCESS METRICS

- **Performance**: Support 100+ concurrent users per document
- **Reliability**: 99.9% uptime with conflict-free editing
- **User Experience**: Sub-100ms latency for real-time updates
- **Scalability**: Handle 10,000+ documents and 1,000+ users

---

## 🔧 DEVELOPMENT NOTES

- Use Redis for session management and real-time state
- Implement proper error handling and logging
- Follow RESTful API design principles
- Ensure data consistency with CRDT algorithms
- Implement comprehensive security measures
- Plan for horizontal scaling from the start
