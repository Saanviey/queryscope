-- department: simple lookup table, no FK dependencies
CREATE TABLE department (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- add department_id to existing employee table (one department per employee)
ALTER TABLE employee ADD COLUMN department_id INT REFERENCES department(department_id);

-- ticket: raised by either a customer or an employee (one of the two FKs will be null per row)
CREATE TABLE ticket (
    ticket_id SERIAL PRIMARY KEY,
    subject VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',   -- open / in_progress / closed
    priority VARCHAR(10) NOT NULL DEFAULT 'medium', -- low / medium / high
    customer_id INT REFERENCES customer(customer_id),
    raised_by_employee_id INT REFERENCES employee(employee_id),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- ticket_assignment: which employee is handling which ticket (join table)
CREATE TABLE ticket_assignment (
    ticket_id INT NOT NULL REFERENCES ticket(ticket_id),
    employee_id INT NOT NULL REFERENCES employee(employee_id),
    assigned_at TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (ticket_id, employee_id)
);

-- sla_log: one row per ticket, tracks whether SLA was met
CREATE TABLE sla_log (
    ticket_id INT PRIMARY KEY REFERENCES ticket(ticket_id),
    due_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    breached BOOLEAN NOT NULL DEFAULT false
);