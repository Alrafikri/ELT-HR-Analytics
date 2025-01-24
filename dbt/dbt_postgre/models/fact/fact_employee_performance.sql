SELECT 
    pr."PerformanceID" as performance_review_id,
    e.employee_id, 
    e.department,
    e.job_role,
    pr."ReviewDate" as review_date, 
    pr."EnvironmentSatisfaction" as environment_satisfaction, 
    pr."JobSatisfaction" as job_satisfaction, 
    pr."RelationshipSatisfaction" as relationship_satisfaction, 
    pr."TrainingOpportunitiesWithinYear" as training_opportunities_year, 
    pr."TrainingOpportunitiesTaken" as training_opportunities_taken, 
    pr."WorkLifeBalance" as work_life_balance, 
    pr."SelfRating" as self_rating, 
    pr."ManagerRating" as manager_rating
FROM 
    {{ source('staging', 'stg_dev_performance_rating') }} as pr
JOIN 
    {{ ref('dim_employee') }} e ON pr."EmployeeID" = e.employee_id