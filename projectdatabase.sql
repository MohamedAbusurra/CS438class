CREATE DATABASE IF NOT EXISTS CollaborationAndMangementTool;

USE CollaborationAndMangementTool ;

CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(200) NOT NULL UNIQUE,
    fullName VARCHAR(120) NULL,
    passwordHash VARCHAR(255) NOT NULL,
    isVerified BOOLEAN NOT NULL DEFAULT FALSE,
    creationDate DATE NULL,
    role ENUM('Team Member', 'Project Manager', 'Supervisor') NOT NULL DEFAULT 'Team Member'
);

CREATE TABLE IF NOT EXISTS projects (
    projectId INT AUTO_INCREMENT PRIMARY KEY,
    projectName VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NULL,
    startDate DATE NULL,
    expectedEndDate DATE NULL,
    status ENUM('active', 'completed', 'pending') NOT NULL DEFAULT 'pending',
    createdBy INT NOT NULL,
    FOREIGN KEY (createdBy) REFERENCES users(userId) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS milestones (
    milestoneId INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    projectId INT NOT NULL,
    endDate DATE NULL,
    status ENUM('Not Started', 'In Progress', 'Completed') NOT NULL DEFAULT 'Not Started',
    completionPercentage INT NOT NULL DEFAULT 0,
    description TEXT NULL,
    FOREIGN KEY (projectId) REFERENCES projects(projectId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    taskId INT AUTO_INCREMENT PRIMARY KEY,
    projectId INT NOT NULL,
    milestoneId INT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    importance ENUM('normal', 'high') NOT NULL DEFAULT 'normal',
    status ENUM('not begun', 'in progress', 'finished') NOT NULL DEFAULT 'not begun',
    dueDate DATE NULL,
    assignedTo INT NULL,
    createdBy INT NOT NULL,
    startDate DATE NULL,
    estimatedDuration INT NULL,
    actualStartDate DATE NULL,
    actualEndDate DATE NULL,
    FOREIGN KEY (projectId) REFERENCES projects(projectId) ON DELETE CASCADE,
    FOREIGN KEY (milestoneId) REFERENCES milestones(milestoneId) ON DELETE SET NULL,
    FOREIGN KEY (assignedTo) REFERENCES users(userId) ON DELETE SET NULL,
    FOREIGN KEY (createdBy) REFERENCES users(userId) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS taskDependencies (
    dependencyId INT AUTO_INCREMENT PRIMARY KEY,
    taskId INT NOT NULL,
    dependsOnTaskId INT NOT NULL,
    dependencyType ENUM('Finish Then Start', 'Start After Start', 'Finish After Finish', 'Finish After Start') NOT NULL DEFAULT 'Finish Then Start',
    FOREIGN KEY (taskId) REFERENCES tasks(taskId) ON DELETE CASCADE,
    FOREIGN KEY (dependsOnTaskId) REFERENCES tasks(taskId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projectMembers (
    projectMemberId INT AUTO_INCREMENT PRIMARY KEY,
    projectId INT NOT NULL,
    userId INT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Team Member',
    UNIQUE KEY uk_project_user (projectId, userId),
    FOREIGN KEY (projectId) REFERENCES projects(projectId) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS files (
    fileId INT AUTO_INCREMENT PRIMARY KEY,
    projectId INT NOT NULL,
    fileName VARCHAR(255) NOT NULL,
    filePath VARCHAR(512) NOT NULL UNIQUE,
    uploadedBy INT NULL,
    uploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projectId) REFERENCES projects(projectId) ON DELETE CASCADE,
    FOREIGN KEY (uploadedBy) REFERENCES users(userId) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fileVersions (
    versionId INT AUTO_INCREMENT PRIMARY KEY,
    fileId INT NOT NULL,
    versionNumber INT NOT NULL,
    versionPath VARCHAR(512) NOT NULL UNIQUE,
    changeTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changedBy INT NULL,
    UNIQUE KEY uk_file_version (fileId, versionNumber),
    FOREIGN KEY (fileId) REFERENCES files(fileId) ON DELETE CASCADE,
    FOREIGN KEY (changedBy) REFERENCES users(userId) ON DELETE SET NULL
);