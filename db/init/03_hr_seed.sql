-- departments: a few realistic ones, no dependencies
INSERT INTO department (name) VALUES
    ('Support'), ('Engineering'), ('Sales');

-- assign existing employees to departments (employee_id 1-5, department_id 1-3)
UPDATE employee SET department_id = 1 WHERE employee_id IN (1, 2);
UPDATE employee SET department_id = 2 WHERE employee_id IN (3, 4);
UPDATE employee SET department_id = 3 WHERE employee_id = 5;

-- tickets: mix of customer-raised and employee-raised, varied status/priority
INSERT INTO ticket (subject, status, priority, customer_id, raised_by_employee_id) VALUES
    ('Cannot access account', 'open', 'high', 1, NULL),
    ('Refund request for invoice', 'in_progress', 'medium', 2, NULL),
    ('Internal server outage', 'open', 'high', NULL, 3),
    ('Playlist sync bug', 'closed', 'low', 4, NULL),
    ('Employee laptop replacement', 'open', 'medium', NULL, 5);

-- ticket_assignment: which employee is handling which ticket
INSERT INTO ticket_assignment (ticket_id, employee_id) VALUES
    (1, 1), (2, 2), (3, 3), (4, 1), (5, 4);

-- sla_log: due dates, some breached, some not, one still unresolved
INSERT INTO sla_log (ticket_id, due_at, resolved_at, breached) VALUES
    (1, now() + interval '1 day', NULL, false),
    (2, now() - interval '1 day', now(), true),
    (3, now() + interval '2 hours', NULL, false),
    (4, now() - interval '3 days', now() - interval '2 days', false),
    (5, now() + interval '1 day', NULL, false);