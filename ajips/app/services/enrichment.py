from __future__ import annotations

from typing import Dict, List, Set

# Comprehensive hidden skill mappings based on co-occurrence patterns
HIDDEN_SKILL_MAP = {
    # Cloud Platforms
    "kubernetes": ["helm", "rbac", "service mesh", "istio", "ingress controllers", "pod security", "kubectl"],
    "aws": ["iam", "vpc", "cloudwatch", "s3", "ec2", "lambda", "cloudformation", "eks", "rds"],
    "azure": ["azure ad", "arm templates", "azure devops", "aks", "azure functions"],
    "gcp": ["gke", "cloud functions", "bigquery", "cloud storage", "iam", "stackdriver"],
    "docker": ["containerization", "dockerfile", "docker compose", "image optimization", "multi-stage builds"],
    
    # Programming Languages
    "python": ["testing", "packaging", "type hints", "virtual environments", "pip", "pytest", "pep 8"],
    "javascript": ["es6+", "async/await", "promises", "closures", "event loop", "npm", "webpack"],
    "typescript": ["type safety", "interfaces", "generics", "decorators", "tsconfig"],
    "java": ["jvm", "maven", "gradle", "spring framework", "junit", "design patterns"],
    "go": ["goroutines", "channels", "interfaces", "error handling", "go modules"],
    
    # Frontend Frameworks
    "react": ["state management", "component design", "hooks", "jsx", "virtual dom", "react router", "context api"],
    "angular": ["typescript", "rxjs", "dependency injection", "components", "services", "routing"],
    "vue": ["vuex", "vue router", "composition api", "single file components"],
    
    # Backend Frameworks
    "django": ["orm", "migrations", "middleware", "authentication", "rest framework"],
    "flask": ["blueprints", "jinja2", "sqlalchemy", "wsgi"],
    "fastapi": ["async", "pydantic", "dependency injection", "openapi", "swagger"],
    "express": ["middleware", "routing", "error handling", "authentication"],
    
    # Databases
    "sql": ["query optimization", "data modeling", "indexing", "normalization", "joins", "transactions"],
    "postgresql": ["pgadmin", "psql", "jsonb", "full-text search", "replication", "partitioning"],
    "mongodb": ["aggregation", "indexing", "sharding", "replica sets", "mongoose"],
    "redis": ["caching", "pub/sub", "data structures", "persistence", "clustering"],
    
    # DevOps & CI/CD
    "jenkins": ["pipelines", "groovy", "plugins", "build automation", "continuous integration"],
    "github actions": ["workflows", "yaml", "secrets management", "matrix builds"],
    "terraform": ["infrastructure as code", "state management", "modules", "providers"],
    "ansible": ["playbooks", "roles", "inventory", "yaml", "idempotency"],
    
    # Data & Analytics
    "spark": ["rdd", "dataframes", "spark sql", "pyspark", "cluster computing"],
    "airflow": ["dags", "operators", "scheduling", "task dependencies", "xcom"],
    "kafka": ["producers", "consumers", "topics", "partitions", "stream processing"],
    
    # Methodologies
    "microservices": ["api gateway", "service discovery", "circuit breaker", "distributed tracing"],
    "rest": ["http methods", "status codes", "api design", "versioning", "authentication"],
    "graphql": ["schema", "resolvers", "queries", "mutations", "subscriptions"],
    "agile": ["sprint planning", "retrospectives", "user stories", "backlog grooming"],
}

# Role-based skill templates
ROLE_TEMPLATES = {
    "data scientist": {
        "core": ["python", "sql", "statistics", "machine learning"],
        "hidden": ["data cleaning", "feature engineering", "model evaluation", "a/b testing",
                  "data visualization", "statistical analysis", "hypothesis testing"]
    },
    "backend engineer": {
        "core": ["python", "java", "sql", "api"],
        "hidden": ["database design", "caching strategies", "api versioning", "error handling",
                  "logging", "monitoring", "performance optimization", "security best practices"]
    },
    "frontend developer": {
        "core": ["javascript", "react", "html", "css"],
        "hidden": ["responsive design", "cross-browser compatibility", "accessibility", "seo",
                  "performance optimization", "state management", "component architecture"]
    },
    "devops engineer": {
        "core": ["docker", "kubernetes", "aws", "terraform"],
        "hidden": ["monitoring", "logging", "incident response", "capacity planning",
                  "security hardening", "disaster recovery", "automation"]
    },
    "full stack developer": {
        "core": ["javascript", "react", "node.js", "sql"],
        "hidden": ["api design", "database optimization", "authentication", "deployment",
                  "testing", "version control", "code review"]
    },
    "machine learning engineer": {
        "core": ["python", "tensorflow", "pytorch", "machine learning"],
        "hidden": ["model deployment", "mlops", "feature stores", "model monitoring",
                  "hyperparameter tuning", "distributed training", "model versioning"]
    },
    "cloud architect": {
        "core": ["aws", "azure", "gcp", "terraform"],
        "hidden": ["cost optimization", "security architecture", "high availability",
                  "disaster recovery", "compliance", "network design", "migration strategies"]
    }
}

# Skill clustering - skills that often appear together
SKILL_CLUSTERS = {
    "modern_web_stack": ["react", "typescript", "next.js", "tailwind", "vercel"],
    "python_data_stack": ["python", "pandas", "numpy", "scikit-learn", "jupyter"],
    "aws_cloud_stack": ["aws", "ec2", "s3", "lambda", "cloudformation"],
    "devops_stack": ["docker", "kubernetes", "jenkins", "terraform", "ansible"],
    "mern_stack": ["mongodb", "express", "react", "node.js"],
    "data_engineering": ["spark", "airflow", "kafka", "python", "sql"],
    "ml_stack": ["python", "tensorflow", "pytorch", "scikit-learn", "pandas"]
}


def infer_hidden_skills(explicit_skills: List[str]) -> List[str]:
    """
    Infer hidden skills based on explicit skills using multiple strategies:
    1. Direct skill mappings
    2. Role-based templates
    3. Skill clustering
    """
    inferred: Set[str] = set()
    
    # Strategy 1: Direct skill mappings
    for skill in explicit_skills:
        skill_lower = skill.lower()
        if skill_lower in HIDDEN_SKILL_MAP:
            inferred.update(HIDDEN_SKILL_MAP[skill_lower])
    
    # Strategy 2: Role-based inference
    role_keywords = {
        "data scientist": ["data", "scientist", "analytics", "ml"],
        "backend engineer": ["backend", "back-end", "server", "api"],
        "frontend developer": ["frontend", "front-end", "ui", "react"],
        "devops engineer": ["devops", "infrastructure", "cloud", "deployment"],
        "full stack developer": ["full stack", "fullstack", "full-stack"],
        "machine learning engineer": ["machine learning", "ml engineer", "ai"],
        "cloud architect": ["cloud architect", "solutions architect"]
    }
    
    # Detect likely role from skills
    detected_roles = []
    skill_text = " ".join(explicit_skills).lower()
    for role, keywords in role_keywords.items():
        if any(keyword in skill_text for keyword in keywords):
            detected_roles.append(role)
    
    # Add role-specific hidden skills
    for role in detected_roles:
        if role in ROLE_TEMPLATES:
            inferred.update(ROLE_TEMPLATES[role]["hidden"])
    
    # Strategy 3: Skill clustering
    for cluster_name, cluster_skills in SKILL_CLUSTERS.items():
        # If we have 2+ skills from a cluster, infer the rest
        matches = sum(1 for skill in explicit_skills if skill.lower() in cluster_skills)
        if matches >= 2:
            inferred.update(cluster_skills)
    
    # Remove skills that are already explicit
    explicit_lower = {skill.lower() for skill in explicit_skills}
    inferred = {skill for skill in inferred if skill.lower() not in explicit_lower}
    
    return sorted(list(inferred))


def get_skill_relationships(skill: str) -> Dict[str, List[str]]:
    """
    Get related skills for a given skill.
    Returns a dictionary with categories: prerequisites, complementary, advanced
    """
    skill_lower = skill.lower()
    
    relationships = {
        "prerequisites": [],
        "complementary": [],
        "advanced": []
    }
    
    # Define some common relationships
    prerequisites_map = {
        "react": ["javascript", "html", "css"],
        "kubernetes": ["docker", "containerization"],
        "terraform": ["infrastructure as code", "cloud platforms"],
        "machine learning": ["python", "statistics", "linear algebra"],
    }
    
    complementary_map = {
        "react": ["redux", "react router", "next.js"],
        "python": ["pip", "virtual environments", "pytest"],
        "docker": ["docker compose", "kubernetes"],
    }
    
    advanced_map = {
        "javascript": ["typescript", "webpack", "babel"],
        "sql": ["query optimization", "database tuning"],
        "python": ["async programming", "metaclasses", "decorators"],
    }
    
    if skill_lower in prerequisites_map:
        relationships["prerequisites"] = prerequisites_map[skill_lower]
    if skill_lower in complementary_map:
        relationships["complementary"] = complementary_map[skill_lower]
    if skill_lower in advanced_map:
        relationships["advanced"] = advanced_map[skill_lower]
    
    return relationships
