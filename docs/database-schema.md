# Database Schema Design

## Overview

The Collaborative Document Editor uses a hybrid database approach:
- **PostgreSQL**: Persistent storage for metadata, user data, and document snapshots
- **Redis**: Real-time operations, session management, and caching

## PostgreSQL Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Organizations Table
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_owner_id ON organizations(owner_id);
```

### Organization Members Table
```sql
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

CREATE INDEX idx_org_members_org_id ON organization_members(organization_id);
CREATE INDEX idx_org_members_user_id ON organization_members(user_id);
```

### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT DEFAULT '',
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    template_category VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_edited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    operations_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted'))
);

CREATE INDEX idx_documents_owner_id ON documents(owner_id);
CREATE INDEX idx_documents_organization_id ON documents(organization_id);
CREATE INDEX idx_documents_is_public ON documents(is_public);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_updated_at ON documents(updated_at);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_title_search ON documents USING GIN(to_tsvector('english', title));
```

### Document Permissions Table
```sql
CREATE TABLE document_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    permission VARCHAR(20) NOT NULL CHECK (permission IN ('owner', 'editor', 'commenter', 'viewer')),
    granted_by UUID NOT NULL REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(document_id, user_id),
    UNIQUE(document_id, organization_id),
    CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE INDEX idx_doc_permissions_doc_id ON document_permissions(document_id);
CREATE INDEX idx_doc_permissions_user_id ON document_permissions(user_id);
CREATE INDEX idx_doc_permissions_org_id ON document_permissions(organization_id);
```

### Document Versions Table
```sql
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    operations_count INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    character_count INTEGER NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    changes_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    snapshot_url TEXT,
    UNIQUE(document_id, version)
);

CREATE INDEX idx_doc_versions_doc_id ON document_versions(document_id);
CREATE INDEX idx_doc_versions_version ON document_versions(document_id, version);
CREATE INDEX idx_doc_versions_created_at ON document_versions(created_at);
```

### Document Operations Table
```sql
CREATE TABLE document_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    operation_id VARCHAR(100) NOT NULL,
    operation_type VARCHAR(20) NOT NULL CHECK (operation_type IN ('insert', 'delete', 'format', 'comment')),
    position_site_id VARCHAR(100) NOT NULL,
    position_clock INTEGER NOT NULL,
    position_path INTEGER[] NOT NULL,
    content TEXT DEFAULT '',
    attributes JSONB DEFAULT '{}',
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER NOT NULL,
    UNIQUE(document_id, operation_id)
);

CREATE INDEX idx_doc_ops_doc_id ON document_operations(document_id);
CREATE INDEX idx_doc_ops_author_id ON document_operations(author_id);
CREATE INDEX idx_doc_ops_created_at ON document_operations(created_at);
CREATE INDEX idx_doc_ops_version ON document_operations(document_id, version);
CREATE INDEX idx_doc_ops_position ON document_operations(document_id, position_site_id, position_clock);
```

### Comments Table
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    position_site_id VARCHAR(100) NOT NULL,
    position_clock INTEGER NOT NULL,
    position_path INTEGER[] NOT NULL,
    end_position_site_id VARCHAR(100),
    end_position_clock INTEGER,
    end_position_path INTEGER[],
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_comments_doc_id ON comments(document_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
CREATE INDEX idx_comments_resolved ON comments(resolved);
CREATE INDEX idx_comments_position ON comments(document_id, position_site_id, position_clock);
```

### Comment Reactions Table
```sql
CREATE TABLE comment_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reaction_type VARCHAR(20) NOT NULL CHECK (reaction_type IN ('like', 'dislike', 'heart', 'laugh', 'angry')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(comment_id, user_id)
);

CREATE INDEX idx_comment_reactions_comment_id ON comment_reactions(comment_id);
CREATE INDEX idx_comment_reactions_user_id ON comment_reactions(user_id);
```

### Files Table
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_url TEXT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    width INTEGER,
    height INTEGER,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX idx_files_document_id ON files(document_id);
CREATE INDEX idx_files_mime_type ON files(mime_type);
CREATE INDEX idx_files_created_at ON files(created_at);
```

### Document Shares Table
```sql
CREATE TABLE document_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    share_token VARCHAR(100) UNIQUE NOT NULL,
    permission VARCHAR(20) NOT NULL CHECK (permission IN ('viewer', 'commenter', 'editor')),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_doc_shares_token ON document_shares(share_token);
CREATE INDEX idx_doc_shares_doc_id ON document_shares(document_id);
CREATE INDEX idx_doc_shares_active ON document_shares(is_active);
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

## Redis Data Structures

### Document CRDT State
```redis
# Hash: Document CRDT state
HSET doc:{document_id}:state site_id_1 clock_1 "operation_data_1"
HSET doc:{document_id}:state site_id_2 clock_2 "operation_data_2"
EXPIRE doc:{document_id}:state 3600  # 1 hour TTL
```

### Operation Logs
```redis
# Sorted Set: Operations ordered by timestamp
ZADD doc:{document_id}:ops timestamp_1 "operation_1"
ZADD doc:{document_id}:ops timestamp_2 "operation_2"
EXPIRE doc:{document_id}:ops 3600
```

### Active User Sessions
```redis
# Set: Active users in document
SADD doc:{document_id}:users user_id_1 user_id_2 user_id_3
EXPIRE doc:{document_id}:users 300  # 5 minutes TTL
```

### User Cursor Positions
```redis
# Hash: User cursor positions
HSET doc:{document_id}:cursors user_id_1 "cursor_data_1"
HSET doc:{document_id}:cursors user_id_2 "cursor_data_2"
EXPIRE doc:{document_id}:cursors 60  # 1 minute TTL
```

### WebSocket Connections
```redis
# Hash: WebSocket connection mapping
HSET ws:connections connection_id_1 "user_id_1"
HSET ws:connections connection_id_2 "user_id_2"
EXPIRE ws:connections 300
```

### Document Locks
```redis
# String: Document edit locks
SET doc:{document_id}:lock user_id_1 EX 30  # 30 seconds TTL
```

### Rate Limiting
```redis
# String: Rate limit counters
SET rate_limit:user:{user_id}:api 1 EX 60
SET rate_limit:user:{user_id}:ws 1 EX 60
```

### Cache Keys
```redis
# String: Cached document content
SET cache:doc:{document_id}:content "document_content" EX 300

# Hash: Cached user data
HSET cache:user:{user_id} name "John Doe" email "john@example.com"
EXPIRE cache:user:{user_id} 600
```

### Pub/Sub Channels
```redis
# Real-time operation broadcasting
PUBLISH doc:{document_id}:ops "operation_data"

# User presence updates
PUBLISH doc:{document_id}:presence "user_joined_data"

# Cursor position updates
PUBLISH doc:{document_id}:cursors "cursor_update_data"
```

## Database Migrations

### Migration 001: Initial Schema
```sql
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted'))
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT DEFAULT '',
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    template_category VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_edited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    operations_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted'))
);

-- Create document indexes
CREATE INDEX idx_documents_owner_id ON documents(owner_id);
CREATE INDEX idx_documents_organization_id ON documents(organization_id);
CREATE INDEX idx_documents_is_public ON documents(is_public);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_updated_at ON documents(updated_at);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_title_search ON documents USING GIN(to_tsvector('english', title));
```

### Migration 002: Add Document Operations
```sql
-- Create document operations table
CREATE TABLE document_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    operation_id VARCHAR(100) NOT NULL,
    operation_type VARCHAR(20) NOT NULL CHECK (operation_type IN ('insert', 'delete', 'format', 'comment')),
    position_site_id VARCHAR(100) NOT NULL,
    position_clock INTEGER NOT NULL,
    position_path INTEGER[] NOT NULL,
    content TEXT DEFAULT '',
    attributes JSONB DEFAULT '{}',
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER NOT NULL,
    UNIQUE(document_id, operation_id)
);

-- Create indexes
CREATE INDEX idx_doc_ops_doc_id ON document_operations(document_id);
CREATE INDEX idx_doc_ops_author_id ON document_operations(author_id);
CREATE INDEX idx_doc_ops_created_at ON document_operations(created_at);
CREATE INDEX idx_doc_ops_version ON document_operations(document_id, version);
CREATE INDEX idx_doc_ops_position ON document_operations(document_id, position_site_id, position_clock);
```

## Data Consistency Strategies

### 1. Eventual Consistency
- CRDT operations ensure eventual consistency across all clients
- Redis provides real-time synchronization
- PostgreSQL provides persistent storage with ACID guarantees

### 2. Conflict Resolution
- CRDT algorithms handle automatic conflict resolution
- Last-write-wins for metadata conflicts
- Operational transformation for content conflicts

### 3. Data Synchronization
- Real-time sync via Redis Pub/Sub
- Periodic snapshots to PostgreSQL
- Background reconciliation processes

### 4. Backup and Recovery
- Daily PostgreSQL backups
- Redis persistence configuration
- Point-in-time recovery capabilities

## Performance Optimization

### 1. Indexing Strategy
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- GIN indexes for JSONB and array columns

### 2. Partitioning
- Partition document_operations by date
- Partition audit_logs by month
- Use table inheritance for large tables

### 3. Caching Strategy
- Redis for frequently accessed data
- Application-level caching for user sessions
- CDN for static assets

### 4. Connection Pooling
- PgBouncer for PostgreSQL connection pooling
- Redis connection pooling
- WebSocket connection management
