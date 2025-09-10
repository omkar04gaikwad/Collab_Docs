# Database Schema Documentation

## Database Choice Rationale

### Why PostgreSQL (RDBMS) over NoSQL?

#### **Advantages of PostgreSQL for Collaborative Docs:**

1. **ACID Compliance**
   - Ensures data consistency during concurrent operations
   - Critical for document versioning and user permissions
   - Prevents data corruption in multi-user scenarios

2. **Complex Relationships**
   - Documents have complex relationships (users, permissions, versions, operations)
   - Foreign key constraints ensure referential integrity
   - Easier to maintain data consistency across related tables

3. **Advanced Querying**
   - Complex queries for document search, filtering, and analytics
   - Full-text search capabilities for document content
   - Aggregation functions for user activity and document statistics

4. **Mature Ecosystem**
   - Robust backup and recovery mechanisms
   - Excellent monitoring and performance tuning tools
   - Strong community support and documentation

5. **JSON Support**
   - Native JSON/JSONB support for storing CRDT operations
   - Can store semi-structured data when needed
   - Best of both worlds: relational structure + flexible data

#### **Why Not Pure NoSQL?**

1. **Data Consistency Issues**
   - NoSQL eventual consistency can cause conflicts in collaborative editing
   - Difficult to maintain referential integrity
   - Complex conflict resolution for document operations

2. **Limited Querying**
   - Difficult to perform complex joins and aggregations
   - Limited support for ACID transactions across documents
   - Harder to implement sophisticated permission systems

#### **Hybrid Approach Consideration**

**Current Architecture: PostgreSQL + Redis**
- **PostgreSQL**: Persistent storage, complex queries, ACID compliance
- **Redis**: Caching, session management, real-time state, pub/sub for WebSocket

This hybrid approach leverages the strengths of both:
- PostgreSQL for reliable data persistence
- Redis for high-performance real-time operations
- Best performance and reliability combination

---

## Database Schema Design

### Table Relationships Overview
```
Users (1) ──→ (M) Documents
Users (1) ──→ (M) Document_Permissions
Users (1) ──→ (M) Document_Operations
Users (1) ──→ (M) User_Sessions
Users (1) ──→ (M) Document_Collaborators
Users (1) ──→ (M) Document_Comments

Documents (1) ──→ (M) Document_Versions
Documents (1) ──→ (M) Document_Permissions
Documents (1) ──→ (M) Document_Operations
Documents (1) ──→ (M) Document_Collaborators
Documents (1) ──→ (M) Document_Comments
```

---

## Detailed Table Schemas

### 1. Users Table
**Purpose**: Store user account information and profiles

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | - | User's unique username |
| email | VARCHAR(255) | UNIQUE, NOT NULL | - | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | - | BCrypt encrypted password |
| first_name | VARCHAR(100) | NOT NULL | - | User's first name |
| last_name | VARCHAR(100) | NOT NULL | - | User's last name |
| avatar_url | VARCHAR(500) | NULL | NULL | Profile picture URL |
| is_email_verified | BOOLEAN | NOT NULL | FALSE | Email verification status |
| is_active | BOOLEAN | NOT NULL | TRUE | Account status |
| created_at | TIMESTAMP | NOT NULL | NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update time |
| last_login | TIMESTAMP | NULL | NULL | Last login time |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE INDEX (username)
- UNIQUE INDEX (email)
- INDEX (is_active)
- INDEX (created_at)

---

### 2. Documents Table
**Purpose**: Store document metadata and content

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Unique document identifier |
| title | VARCHAR(255) | NOT NULL | - | Document title |
| content | JSONB | NULL | NULL | Document content (CRDT structure) |
| owner_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Document owner |
| is_public | BOOLEAN | NOT NULL | FALSE | Public visibility |
| is_archived | BOOLEAN | NOT NULL | FALSE | Archive status |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update time |
| last_modified_by | BIGINT | FOREIGN KEY (users.id) | NULL | Last editor |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (owner_id) REFERENCES users(id)
- FOREIGN KEY (last_modified_by) REFERENCES users(id)
- INDEX (owner_id)
- INDEX (is_public)
- INDEX (is_archived)
- INDEX (created_at)
- INDEX (updated_at)
- GIN INDEX (content) -- For JSONB queries

---

### 3. Document_Versions Table
**Purpose**: Version control and document history

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Version identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id), NOT NULL | - | Parent document |
| version_number | INTEGER | NOT NULL | - | Sequential version number |
| content_snapshot | JSONB | NOT NULL | - | Content at this version |
| change_summary | VARCHAR(500) | NULL | NULL | Description of changes |
| created_by | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Version creator |
| created_at | TIMESTAMP | NOT NULL | NOW() | Version creation time |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
- FOREIGN KEY (created_by) REFERENCES users(id)
- UNIQUE INDEX (document_id, version_number)
- INDEX (document_id)
- INDEX (created_at)

---

### 4. Document_Permissions Table
**Purpose**: Access control and sharing permissions

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Permission identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id), NOT NULL | - | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | User with permission |
| permission_type | VARCHAR(20) | NOT NULL, CHECK (permission_type IN ('READ', 'WRITE', 'ADMIN')) | - | Permission level |
| granted_by | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Permission granter |
| granted_at | TIMESTAMP | NOT NULL | NOW() | Permission grant time |
| expires_at | TIMESTAMP | NULL | NULL | Permission expiration |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- FOREIGN KEY (granted_by) REFERENCES users(id)
- UNIQUE INDEX (document_id, user_id)
- INDEX (document_id)
- INDEX (user_id)
- INDEX (permission_type)

---

### 5. Document_Operations Table
**Purpose**: CRDT operations for conflict-free editing

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Operation identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id), NOT NULL | - | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Operation author |
| operation_type | VARCHAR(20) | NOT NULL, CHECK (operation_type IN ('INSERT', 'DELETE', 'RETAIN')) | - | CRDT operation type |
| position | INTEGER | NOT NULL | - | Character position |
| content | TEXT | NULL | NULL | Content to insert/delete |
| operation_id | VARCHAR(100) | UNIQUE, NOT NULL | - | CRDT operation ID |
| timestamp | BIGINT | NOT NULL | - | Logical timestamp |
| created_at | TIMESTAMP | NOT NULL | NOW() | Operation creation time |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
- FOREIGN KEY (user_id) REFERENCES users(id)
- UNIQUE INDEX (operation_id)
- INDEX (document_id)
- INDEX (user_id)
- INDEX (timestamp)
- INDEX (created_at)

---

### 6. User_Sessions Table
**Purpose**: Authentication sessions and security

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Session identifier |
| user_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Session owner |
| session_token | VARCHAR(500) | UNIQUE, NOT NULL | - | JWT token |
| device_info | VARCHAR(255) | NULL | NULL | Device/browser info |
| ip_address | INET | NULL | NULL | Client IP address |
| is_active | BOOLEAN | NOT NULL | TRUE | Session status |
| created_at | TIMESTAMP | NOT NULL | NOW() | Session start time |
| expires_at | TIMESTAMP | NOT NULL | - | Session expiration |
| last_activity | TIMESTAMP | NOT NULL | NOW() | Last activity time |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- UNIQUE INDEX (session_token)
- INDEX (user_id)
- INDEX (is_active)
- INDEX (expires_at)

---

### 7. Document_Collaborators Table
**Purpose**: Real-time collaboration state tracking

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Collaboration identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id), NOT NULL | - | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Collaborator |
| cursor_position | INTEGER | NULL | NULL | Current cursor position |
| selection_start | INTEGER | NULL | NULL | Selection start position |
| selection_end | INTEGER | NULL | NULL | Selection end position |
| is_online | BOOLEAN | NOT NULL | FALSE | Online status |
| last_seen | TIMESTAMP | NOT NULL | NOW() | Last activity time |
| joined_at | TIMESTAMP | NOT NULL | NOW() | Collaboration start time |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- UNIQUE INDEX (document_id, user_id)
- INDEX (document_id)
- INDEX (user_id)
- INDEX (is_online)

---

### 8. Document_Comments Table
**Purpose**: Comments and suggestions on documents

| Column Name | Data Type | Constraints | Default Value | Description |
|-------------|-----------|-------------|---------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | AUTO_INCREMENT | Comment identifier |
| document_id | BIGINT | FOREIGN KEY (documents.id), NOT NULL | - | Target document |
| user_id | BIGINT | FOREIGN KEY (users.id), NOT NULL | - | Comment author |
| content | TEXT | NOT NULL | - | Comment text |
| position | INTEGER | NULL | NULL | Character position |
| is_resolved | BOOLEAN | NOT NULL | FALSE | Resolution status |
| created_at | TIMESTAMP | NOT NULL | NOW() | Comment creation time |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (id)
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
- FOREIGN KEY (user_id) REFERENCES users(id)
- INDEX (document_id)
- INDEX (user_id)
- INDEX (is_resolved)
- INDEX (created_at)

---

## Database Configuration Recommendations

### PostgreSQL Settings
```sql
-- Enable JSONB support
-- Enable full-text search
-- Configure connection pooling
-- Set up replication for high availability
```

### Redis Configuration
```redis
# Session storage
# Real-time collaboration state
# Document operation caching
# WebSocket pub/sub channels
```

### Performance Optimizations
1. **Connection Pooling**: Use HikariCP for database connections
2. **Caching Strategy**: Redis for frequently accessed data
3. **Indexing**: Strategic indexes for common queries
4. **Partitioning**: Consider partitioning large tables by date
5. **Archiving**: Archive old document versions and operations

---

## Data Migration Strategy

### Phase 1: Core Tables
1. Users
2. Documents
3. Document_Permissions

### Phase 2: Collaboration Features
1. Document_Operations
2. Document_Collaborators
3. User_Sessions

### Phase 3: Advanced Features
1. Document_Versions
2. Document_Comments

This approach ensures a stable foundation while adding advanced features incrementally.
