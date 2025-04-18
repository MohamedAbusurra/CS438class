CREATE DATABASE IF NOT EXISTS CollaborationAndMangementTool;

USE CollaborationAndMangementTool ;

CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(100) NOT NULL UNIQUE,
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