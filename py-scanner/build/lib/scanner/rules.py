"""
Types and rule definitions for the tech-stack scanner.

Detection strategies per rule:
  match.files            – marker file / directory existence
  match.extensions       – file extension presence
  match.content_patterns – substring inside a file
  dependencies           – package name in manifest (npm/pip/docker/go/ruby/rust/php)
  dotenv                 – env-var prefix in .env files
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ── Tech types ─────────────────────────────────────────────

TECH_TYPES = (
    "language", "framework", "ui_framework", "ui", "runtime", "tool", "builder",
    "linter", "test", "ci", "hosting", "cloud", "db", "orm", "queue", "storage",
    "ai", "analytics", "monitoring", "auth", "payment", "notification", "cms",
    "saas", "iac", "security", "automation", "ssg", "package_manager",
    "validation", "app", "network", "unknown",
)

# ── Dependency types ───────────────────────────────────────

DEP_TYPES = ("npm", "python", "docker", "golang", "ruby", "rust", "php")


@dataclass
class RuleDependency:
    type: str   # one of DEP_TYPES
    name: str


@dataclass
class ContentPattern:
    file: str
    patterns: list[str]


@dataclass
class RuleMatch:
    files: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    content_patterns: list[ContentPattern] = field(default_factory=list)


@dataclass
class Rule:
    id: str
    name: str
    type: str  # one of TECH_TYPES
    match: Optional[RuleMatch] = None
    dependencies: list[RuleDependency] = field(default_factory=list)
    dotenv: list[str] = field(default_factory=list)


# ── Shorthand helpers ──────────────────────────────────────

def npm(name: str) -> RuleDependency:
    return RuleDependency(type="npm", name=name)

def pip_dep(name: str) -> RuleDependency:
    return RuleDependency(type="python", name=name)

def docker(name: str) -> RuleDependency:
    return RuleDependency(type="docker", name=name)

def gomod(name: str) -> RuleDependency:
    return RuleDependency(type="golang", name=name)

def gem(name: str) -> RuleDependency:
    return RuleDependency(type="ruby", name=name)

def cargo(name: str) -> RuleDependency:
    return RuleDependency(type="rust", name=name)

def composer(name: str) -> RuleDependency:
    return RuleDependency(type="php", name=name)


# ── Helpers for concise rule creation ──────────────────────

def _m(files: list[str] | None = None, extensions: list[str] | None = None,
       content_patterns: list[ContentPattern] | None = None) -> RuleMatch:
    return RuleMatch(
        files=files or [],
        extensions=extensions or [],
        content_patterns=content_patterns or [],
    )


# ═══════════════════════════════════════════════════════════════════
#  RULES CATALOG  (~250 rules)
# ═══════════════════════════════════════════════════════════════════

RULES: list[Rule] = [

    # ── LANGUAGES ──────────────────────────────────────────
    Rule("typescript", "TypeScript", "language", _m(files=["tsconfig.json"], extensions=[".ts", ".tsx"])),
    Rule("javascript", "JavaScript", "language", _m(extensions=[".js", ".jsx", ".mjs", ".cjs"])),
    Rule("python", "Python", "language", _m(files=["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"], extensions=[".py"])),
    Rule("rust", "Rust", "language", _m(files=["Cargo.toml"], extensions=[".rs"])),
    Rule("go", "Go", "language", _m(files=["go.mod", "go.sum"], extensions=[".go"])),
    Rule("java", "Java", "language", _m(files=["pom.xml", "build.gradle", "build.gradle.kts"], extensions=[".java"])),
    Rule("csharp", "C#", "language", _m(extensions=[".cs", ".csproj", ".sln"])),
    Rule("ruby", "Ruby", "language", _m(files=["Gemfile", "Rakefile"], extensions=[".rb"])),
    Rule("php", "PHP", "language", _m(files=["composer.json"], extensions=[".php"])),
    Rule("swift", "Swift", "language", _m(files=["Package.swift"], extensions=[".swift"])),
    Rule("kotlin", "Kotlin", "language", _m(extensions=[".kt", ".kts"])),
    Rule("elixir", "Elixir", "language", _m(files=["mix.exs"], extensions=[".ex", ".exs"])),
    Rule("dart", "Dart", "language", _m(files=["pubspec.yaml"], extensions=[".dart"])),
    Rule("scala", "Scala", "language", _m(files=["build.sbt"], extensions=[".scala"])),
    Rule("cplusplus", "C++", "language", _m(files=["CMakeLists.txt", "Makefile"], extensions=[".cpp", ".cxx", ".cc", ".hpp"])),
    Rule("c", "C", "language", _m(extensions=[".c", ".h"])),
    Rule("lua", "Lua", "language", _m(extensions=[".lua"])),
    Rule("r", "R", "language", _m(extensions=[".R", ".Rmd"])),
    Rule("haskell", "Haskell", "language", _m(files=["stack.yaml", "cabal.project"], extensions=[".hs"])),
    Rule("perl", "Perl", "language", _m(extensions=[".pl", ".pm"])),
    Rule("bash", "Bash", "language", _m(extensions=[".sh", ".bash"])),
    Rule("scss", "SCSS", "language", _m(extensions=[".scss", ".sass"])),
    Rule("css", "CSS", "language", _m(extensions=[".css"])),

    # ── UI FRAMEWORKS ─────────────────────────────────────
    Rule("react", "React", "ui_framework", dependencies=[npm("react")]),
    Rule("vue", "Vue", "ui_framework", _m(extensions=[".vue"]), dependencies=[npm("vue")]),
    Rule("angular", "Angular", "ui_framework", _m(files=["angular.json"]), dependencies=[npm("@angular/core")]),
    Rule("svelte", "Svelte", "ui_framework", _m(extensions=[".svelte"]), dependencies=[npm("svelte")]),
    Rule("solid", "SolidJS", "ui_framework", dependencies=[npm("solid-js")]),
    Rule("preact", "Preact", "ui_framework", dependencies=[npm("preact")]),
    Rule("htmx", "htmx", "ui_framework", dependencies=[npm("htmx.org")]),
    Rule("alpine", "Alpine.js", "ui_framework", dependencies=[npm("alpinejs")]),
    Rule("lit", "Lit", "ui_framework", dependencies=[npm("lit")]),
    Rule("ember", "Ember.js", "ui_framework", dependencies=[npm("ember-source")]),
    Rule("qwik", "Qwik", "ui_framework", dependencies=[npm("@builder.io/qwik")]),
    Rule("stencil", "Stencil", "ui_framework", dependencies=[npm("@stencil/core")]),

    # ── FRAMEWORKS ─────────────────────────────────────────
    Rule("nextjs", "Next.js", "framework", _m(files=["next.config.js", "next.config.mjs", "next.config.ts"]), dependencies=[npm("next")]),
    Rule("nuxt", "Nuxt", "framework", _m(files=["nuxt.config.js", "nuxt.config.ts"]), dependencies=[npm("nuxt")]),
    Rule("sveltekit", "SvelteKit", "framework", dependencies=[npm("@sveltejs/kit")]),
    Rule("remix", "Remix", "framework", dependencies=[npm("@remix-run/node"), npm("@remix-run/react")]),
    Rule("astro", "Astro", "framework", _m(files=["astro.config.mjs", "astro.config.ts"]), dependencies=[npm("astro")]),
    Rule("express", "Express", "framework", dependencies=[npm("express")]),
    Rule("fastify", "Fastify", "framework", dependencies=[npm("fastify")]),
    Rule("nestjs", "NestJS", "framework", dependencies=[npm("@nestjs/core")]),
    Rule("hono", "Hono", "framework", dependencies=[npm("hono")]),
    Rule("koa", "Koa", "framework", dependencies=[npm("koa")]),
    Rule("adonis", "AdonisJS", "framework", dependencies=[npm("@adonisjs/core")]),
    Rule("elysia", "Elysia", "framework", dependencies=[npm("elysia")]),
    Rule("blitz", "Blitz.js", "framework", dependencies=[npm("blitz")]),
    Rule("redwood", "RedwoodJS", "framework", dependencies=[npm("@redwoodjs/core")]),
    Rule("meteor", "Meteor", "framework", _m(files=[".meteor"])),
    Rule("django", "Django", "framework", _m(files=["manage.py"]), dependencies=[pip_dep("django"), pip_dep("Django")]),
    Rule("flask", "Flask", "framework", dependencies=[pip_dep("flask"), pip_dep("Flask")]),
    Rule("fastapi", "FastAPI", "framework", dependencies=[pip_dep("fastapi")]),
    Rule("rails", "Ruby on Rails", "framework", _m(files=["config/routes.rb", "bin/rails"]), dependencies=[gem("rails")]),
    Rule("laravel", "Laravel", "framework", _m(files=["artisan"]), dependencies=[composer("laravel/framework")]),
    Rule("symfony", "Symfony", "framework", dependencies=[composer("symfony/framework-bundle")]),
    Rule("spring", "Spring", "framework", _m(content_patterns=[
        ContentPattern("pom.xml", ["spring-boot", "spring-framework"]),
        ContentPattern("build.gradle", ["spring-boot", "spring-framework"]),
    ])),
    Rule("dotnet", ".NET / ASP.NET", "framework", _m(files=["appsettings.json", "Startup.cs", "Program.cs"], extensions=[".csproj"])),
    Rule("tauri", "Tauri", "framework", _m(files=["src-tauri"]), dependencies=[npm("@tauri-apps/cli")]),
    Rule("electron", "Electron", "framework", dependencies=[npm("electron")]),

    # ── UI LIBRARIES ───────────────────────────────────────
    Rule("tailwind", "Tailwind CSS", "ui", _m(files=["tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs"]), dependencies=[npm("tailwindcss")]),
    Rule("shadcn", "shadcn/ui", "ui", _m(files=["components.json"])),
    Rule("materialui", "Material UI", "ui", dependencies=[npm("@mui/material")]),
    Rule("chakra", "Chakra UI", "ui", dependencies=[npm("@chakra-ui/react")]),
    Rule("antd", "Ant Design", "ui", dependencies=[npm("antd")]),
    Rule("radix", "Radix UI", "ui", dependencies=[npm("@radix-ui/react-dialog"), npm("@radix-ui/themes")]),
    Rule("headlessui", "Headless UI", "ui", dependencies=[npm("@headlessui/react")]),
    Rule("bootstrap", "Bootstrap", "ui", dependencies=[npm("bootstrap"), npm("react-bootstrap")]),
    Rule("daisyui", "daisyUI", "ui", dependencies=[npm("daisyui")]),
    Rule("mantine", "Mantine", "ui", dependencies=[npm("@mantine/core")]),
    Rule("heroui", "HeroUI", "ui", dependencies=[npm("@heroui/react")]),
    Rule("d3", "D3.js", "ui", dependencies=[npm("d3")]),
    Rule("storybook", "Storybook", "ui", _m(files=[".storybook"]), dependencies=[npm("storybook"), npm("@storybook/react")]),

    # ── SSG ────────────────────────────────────────────────
    Rule("gatsby", "Gatsby", "ssg", dependencies=[npm("gatsby")]),
    Rule("hugo", "Hugo", "ssg", _m(files=["hugo.toml", "hugo.yaml", "config.toml"])),
    Rule("jekyll", "Jekyll", "ssg", _m(files=["_config.yml"]), dependencies=[gem("jekyll")]),
    Rule("docusaurus", "Docusaurus", "ssg", dependencies=[npm("@docusaurus/core")]),
    Rule("vitepress", "VitePress", "ssg", dependencies=[npm("vitepress")]),
    Rule("vuepress", "VuePress", "ssg", dependencies=[npm("vuepress")]),
    Rule("eleventy", "Eleventy", "ssg", _m(files=[".eleventy.js", "eleventy.config.js"]), dependencies=[npm("@11ty/eleventy")]),
    Rule("mkdocs", "MkDocs", "ssg", _m(files=["mkdocs.yml"]), dependencies=[pip_dep("mkdocs")]),
    Rule("hexo", "Hexo", "ssg", dependencies=[npm("hexo")]),
    Rule("mintlify", "Mintlify", "ssg", _m(files=["mint.json"])),

    # ── BUILDERS / BUNDLERS ────────────────────────────────
    Rule("vite", "Vite", "builder", _m(files=["vite.config.js", "vite.config.ts"]), dependencies=[npm("vite")]),
    Rule("webpack", "Webpack", "builder", _m(files=["webpack.config.js", "webpack.config.ts"]), dependencies=[npm("webpack")]),
    Rule("esbuild", "esbuild", "builder", dependencies=[npm("esbuild")]),
    Rule("rollup", "Rollup", "builder", _m(files=["rollup.config.js", "rollup.config.ts"]), dependencies=[npm("rollup")]),
    Rule("swc", "SWC", "builder", dependencies=[npm("@swc/core")]),
    Rule("babel", "Babel", "builder", _m(files=["babel.config.js", ".babelrc", "babel.config.json"]), dependencies=[npm("@babel/core")]),
    Rule("parcel", "Parcel", "builder", dependencies=[npm("parcel")]),
    Rule("turborepo", "Turborepo", "builder", _m(files=["turbo.json"]), dependencies=[npm("turbo")]),
    Rule("nx", "Nx", "builder", _m(files=["nx.json"]), dependencies=[npm("nx")]),
    Rule("rspack", "Rspack", "builder", dependencies=[npm("@rspack/core")]),

    # ── LINTERS / FORMATTERS ───────────────────────────────
    Rule("eslint", "ESLint", "linter", _m(files=[".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml", "eslint.config.js", "eslint.config.mjs", "eslint.config.ts"]), dependencies=[npm("eslint")]),
    Rule("prettier", "Prettier", "linter", _m(files=[".prettierrc", ".prettierrc.json", ".prettierrc.js", "prettier.config.js", "prettier.config.mjs"]), dependencies=[npm("prettier")]),
    Rule("biome", "Biome", "linter", _m(files=["biome.json", "biome.jsonc"]), dependencies=[npm("@biomejs/biome")]),
    Rule("stylelint", "Stylelint", "linter", _m(files=[".stylelintrc", ".stylelintrc.json"]), dependencies=[npm("stylelint")]),
    Rule("oxlint", "oxlint", "linter", dependencies=[npm("oxlint")]),
    Rule("rubocop", "RuboCop", "linter", _m(files=[".rubocop.yml"]), dependencies=[gem("rubocop")]),

    # ── TESTING ────────────────────────────────────────────
    Rule("jest", "Jest", "test", _m(files=["jest.config.js", "jest.config.ts", "jest.config.mjs"]), dependencies=[npm("jest")]),
    Rule("vitest", "Vitest", "test", _m(files=["vitest.config.ts", "vitest.config.js"]), dependencies=[npm("vitest")]),
    Rule("mocha", "Mocha", "test", dependencies=[npm("mocha")]),
    Rule("cypress", "Cypress", "test", _m(files=["cypress.config.js", "cypress.config.ts", "cypress"]), dependencies=[npm("cypress")]),
    Rule("playwright", "Playwright", "test", _m(files=["playwright.config.ts", "playwright.config.js"]), dependencies=[npm("@playwright/test"), npm("playwright"), pip_dep("playwright")]),
    Rule("puppeteer", "Puppeteer", "test", dependencies=[npm("puppeteer")]),
    Rule("selenium", "Selenium", "test", dependencies=[npm("selenium-webdriver"), pip_dep("selenium"), gem("selenium-webdriver")]),
    Rule("testing-library", "Testing Library", "test", dependencies=[npm("@testing-library/react"), npm("@testing-library/jest-dom")]),
    Rule("pytest", "pytest", "test", dependencies=[pip_dep("pytest")]),
    Rule("phpunit", "PHPUnit", "test", _m(files=["phpunit.xml", "phpunit.xml.dist"]), dependencies=[composer("phpunit/phpunit")]),
    Rule("k6", "k6", "test", dependencies=[npm("k6")]),

    # ── VALIDATION ─────────────────────────────────────────
    Rule("zod", "Zod", "validation", dependencies=[npm("zod")]),
    Rule("joi", "Joi", "validation", dependencies=[npm("joi")]),
    Rule("yup", "Yup", "validation", dependencies=[npm("yup")]),
    Rule("valibot", "Valibot", "validation", dependencies=[npm("valibot")]),
    Rule("typebox", "TypeBox", "validation", dependencies=[npm("@sinclair/typebox")]),
    Rule("ajv", "Ajv", "validation", dependencies=[npm("ajv")]),

    # ── ORM / DATA ACCESS ─────────────────────────────────
    Rule("prisma", "Prisma", "orm", _m(files=["schema.prisma", "prisma/schema.prisma"]), dependencies=[npm("prisma"), npm("@prisma/client")]),
    Rule("drizzle", "Drizzle", "orm", dependencies=[npm("drizzle-orm")]),
    Rule("typeorm", "TypeORM", "orm", dependencies=[npm("typeorm")]),
    Rule("sequelize", "Sequelize", "orm", _m(files=[".sequelizerc"]), dependencies=[npm("sequelize")]),
    Rule("knex", "Knex", "orm", dependencies=[npm("knex")]),
    Rule("kysely", "Kysely", "orm", dependencies=[npm("kysely")]),
    Rule("mongoose", "Mongoose", "orm", dependencies=[npm("mongoose")]),
    Rule("sqlalchemy", "SQLAlchemy", "orm", dependencies=[pip_dep("SQLAlchemy"), pip_dep("sqlalchemy")]),
    Rule("gorm", "GORM", "orm", dependencies=[gomod("gorm.io/gorm")]),
    Rule("diesel", "Diesel", "orm", _m(files=["diesel.toml"]), dependencies=[cargo("diesel")]),
    Rule("doctrine", "Doctrine", "orm", dependencies=[composer("doctrine/orm")]),

    # ── CI / CD ────────────────────────────────────────────
    Rule("github-actions", "GitHub Actions", "ci", _m(files=[".github/workflows"])),
    Rule("gitlab-ci", "GitLab CI", "ci", _m(files=[".gitlab-ci.yml"])),
    Rule("jenkins", "Jenkins", "ci", _m(files=["Jenkinsfile"])),
    Rule("circleci", "CircleCI", "ci", _m(files=[".circleci/config.yml", ".circleci"])),
    Rule("travis", "Travis CI", "ci", _m(files=[".travis.yml"])),
    Rule("azure-pipelines", "Azure Pipelines", "ci", _m(files=["azure-pipelines.yml"])),
    Rule("bitbucket-pipelines", "Bitbucket Pipelines", "ci", _m(files=["bitbucket-pipelines.yml"])),
    Rule("appveyor", "AppVeyor", "ci", _m(files=["appveyor.yml", ".appveyor.yml"])),
    Rule("dependabot", "Dependabot", "ci", _m(files=[".github/dependabot.yml"])),
    Rule("renovate", "Renovate", "ci", _m(files=["renovate.json", "renovate.json5", ".renovaterc", ".renovaterc.json"])),
    Rule("codecov", "Codecov", "ci", _m(files=["codecov.yml", ".codecov.yml"])),
    Rule("sonarcloud", "SonarCloud", "ci", _m(files=["sonar-project.properties"])),

    # ── CLOUD PROVIDERS ────────────────────────────────────
    Rule("aws", "AWS", "cloud", _m(files=["serverless.yml", "samconfig.toml", "template.yaml", "cdk.json"]), dependencies=[npm("aws-sdk"), npm("@aws-sdk/client-s3"), pip_dep("boto3")], dotenv=["AWS_"]),
    Rule("gcp", "Google Cloud", "cloud", dependencies=[npm("@google-cloud/storage"), npm("@google-cloud/pubsub"), pip_dep("google-cloud-storage")], dotenv=["GOOGLE_CLOUD_", "GCP_", "GCLOUD_"]),
    Rule("azure", "Azure", "cloud", dependencies=[npm("@azure/storage-blob"), npm("@azure/identity")], dotenv=["AZURE_"]),
    Rule("firebase", "Firebase", "cloud", _m(files=["firebase.json", ".firebaserc"]), dependencies=[npm("firebase"), npm("firebase-admin")], dotenv=["FIREBASE_"]),
    Rule("cloudflare", "Cloudflare", "cloud", _m(files=["wrangler.toml", "wrangler.json"]), dependencies=[npm("wrangler"), npm("@cloudflare/workers-types")]),
    Rule("supabase", "Supabase", "cloud", _m(files=["supabase"]), dependencies=[npm("@supabase/supabase-js")], dotenv=["SUPABASE_", "NEXT_PUBLIC_SUPABASE_"]),
    Rule("heroku", "Heroku", "cloud", _m(files=["Procfile", "app.json"])),
    Rule("flyio", "Fly.io", "cloud", _m(files=["fly.toml"])),
    Rule("railway", "Railway", "cloud", _m(files=["railway.json", "railway.toml"])),
    Rule("dokku", "Dokku", "cloud", _m(files=["DOKKU_SCALE"])),

    # ── HOSTING ────────────────────────────────────────────
    Rule("vercel", "Vercel", "hosting", _m(files=["vercel.json", ".vercel"]), dependencies=[npm("@vercel/analytics")]),
    Rule("netlify", "Netlify", "hosting", _m(files=["netlify.toml", "_redirects"])),
    Rule("github-pages", "GitHub Pages", "hosting", _m(files=["CNAME"])),
    Rule("docker", "Docker", "hosting", _m(files=["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml", ".dockerignore"])),
    Rule("kubernetes", "Kubernetes", "hosting", _m(files=["k8s", "kubernetes", "skaffold.yaml"])),
    Rule("digitalocean", "DigitalOcean", "hosting", _m(files=[".do/app.yaml"]), dotenv=["DIGITALOCEAN_"]),
    Rule("render", "Render", "hosting", _m(files=["render.yaml"])),

    # ── IAC ────────────────────────────────────────────────
    Rule("terraform", "Terraform", "iac", _m(extensions=[".tf"], files=["main.tf", "terraform.tfvars"])),
    Rule("pulumi", "Pulumi", "iac", _m(files=["Pulumi.yaml", "Pulumi.yml"]), dependencies=[npm("@pulumi/pulumi"), pip_dep("pulumi")]),
    Rule("ansible", "Ansible", "iac", _m(files=["ansible.cfg", "playbook.yml"]), dependencies=[pip_dep("ansible")]),
    Rule("helm", "Helm", "iac", _m(files=["Chart.yaml"])),
    Rule("terragrunt", "Terragrunt", "iac", _m(files=["terragrunt.hcl"])),

    # ── DATABASES ──────────────────────────────────────────
    Rule("postgresql", "PostgreSQL", "db", dependencies=[npm("pg"), npm("postgres"), pip_dep("psycopg2"), pip_dep("psycopg"), docker("postgres")], dotenv=["POSTGRES_", "PG_", "DATABASE_URL"]),
    Rule("mysql", "MySQL", "db", dependencies=[npm("mysql"), npm("mysql2"), pip_dep("mysqlclient"), pip_dep("PyMySQL"), docker("mysql")], dotenv=["MYSQL_"]),
    Rule("mongodb", "MongoDB", "db", dependencies=[npm("mongodb"), pip_dep("pymongo"), pip_dep("motor"), docker("mongo")], dotenv=["MONGO_", "MONGODB_"]),
    Rule("redis", "Redis", "db", dependencies=[npm("redis"), npm("ioredis"), pip_dep("redis"), docker("redis"), gomod("github.com/redis/go-redis")], dotenv=["REDIS_"]),
    Rule("sqlite", "SQLite", "db", _m(extensions=[".sqlite", ".db"]), dependencies=[npm("better-sqlite3"), npm("sqlite3"), pip_dep("aiosqlite")]),
    Rule("elasticsearch", "Elasticsearch", "db", dependencies=[npm("@elastic/elasticsearch"), pip_dep("elasticsearch"), docker("elasticsearch")], dotenv=["ELASTIC_", "ELASTICSEARCH_"]),
    Rule("neo4j", "Neo4j", "db", dependencies=[npm("neo4j-driver"), pip_dep("neo4j"), docker("neo4j")]),
    Rule("cassandra", "Cassandra", "db", dependencies=[npm("cassandra-driver"), pip_dep("cassandra-driver"), docker("cassandra")]),
    Rule("clickhouse", "ClickHouse", "db", dependencies=[npm("@clickhouse/client"), docker("clickhouse/clickhouse-server"), pip_dep("clickhouse-connect")]),
    Rule("influxdb", "InfluxDB", "db", dependencies=[npm("@influxdata/influxdb-client"), docker("influxdb")]),
    Rule("mssql", "Microsoft SQL Server", "db", dependencies=[npm("mssql"), npm("tedious"), docker("mcr.microsoft.com/mssql/server")]),
    Rule("mariadb", "MariaDB", "db", dependencies=[npm("mariadb"), docker("mariadb")]),
    Rule("couchbase", "Couchbase", "db", dependencies=[npm("couchbase"), docker("couchbase")]),
    Rule("dynamodb", "DynamoDB", "db", dependencies=[npm("@aws-sdk/client-dynamodb"), npm("dynamoose")], dotenv=["DYNAMODB_"]),
    Rule("cockroachdb", "CockroachDB", "db", dependencies=[docker("cockroachdb/cockroach")]),
    Rule("surrealdb", "SurrealDB", "db", dependencies=[npm("surrealdb.js"), docker("surrealdb/surrealdb")]),
    Rule("duckdb", "DuckDB", "db", dependencies=[npm("duckdb"), pip_dep("duckdb")]),
    Rule("neondb", "Neon", "db", dependencies=[npm("@neondatabase/serverless")], dotenv=["NEON_"]),
    Rule("planetscale", "PlanetScale", "db", dependencies=[npm("@planetscale/database")], dotenv=["PLANETSCALE_"]),
    Rule("turso", "Turso", "db", dependencies=[npm("@libsql/client")], dotenv=["TURSO_"]),
    Rule("meilisearch", "Meilisearch", "db", dependencies=[npm("meilisearch"), docker("getmeili/meilisearch")]),
    Rule("typesense", "Typesense", "db", dependencies=[npm("typesense"), docker("typesense/typesense")]),
    Rule("algolia", "Algolia", "db", dependencies=[npm("algoliasearch")], dotenv=["ALGOLIA_"]),
    # ── Vector DBs ──
    Rule("pinecone", "Pinecone", "db", dependencies=[npm("@pinecone-database/pinecone"), pip_dep("pinecone-client")], dotenv=["PINECONE_"]),
    Rule("chromadb", "ChromaDB", "db", dependencies=[npm("chromadb"), pip_dep("chromadb")]),
    Rule("qdrant", "Qdrant", "db", dependencies=[npm("@qdrant/js-client-rest"), pip_dep("qdrant-client")]),
    Rule("milvus", "Milvus", "db", dependencies=[npm("@zilliz/milvus2-sdk-node"), pip_dep("pymilvus")]),
    Rule("weaviate", "Weaviate", "db", dependencies=[npm("weaviate-ts-client"), pip_dep("weaviate-client")]),

    # ── QUEUE / MESSAGING ─────────────────────────────────
    Rule("rabbitmq", "RabbitMQ", "queue", dependencies=[npm("amqplib"), pip_dep("pika"), docker("rabbitmq")], dotenv=["RABBITMQ_"]),
    Rule("kafka", "Apache Kafka", "queue", dependencies=[npm("kafkajs"), pip_dep("kafka-python"), docker("confluentinc/cp-kafka")], dotenv=["KAFKA_"]),
    Rule("bullmq", "BullMQ", "queue", dependencies=[npm("bullmq"), npm("bull")]),
    Rule("sqs", "AWS SQS", "queue", dependencies=[npm("@aws-sdk/client-sqs")], dotenv=["SQS_"]),
    Rule("nats", "NATS", "queue", dependencies=[npm("nats"), docker("nats")]),
    Rule("celery", "Celery", "queue", dependencies=[pip_dep("celery")]),
    Rule("pubsub", "Google Pub/Sub", "queue", dependencies=[npm("@google-cloud/pubsub")]),

    # ── STORAGE ────────────────────────────────────────────
    Rule("s3", "AWS S3", "storage", dependencies=[npm("@aws-sdk/client-s3"), pip_dep("boto3")], dotenv=["S3_", "AWS_S3_"]),
    Rule("cloudflare-r2", "Cloudflare R2", "storage", dependencies=[npm("@cloudflare/r2")]),
    Rule("cloudinary", "Cloudinary", "storage", dependencies=[npm("cloudinary")], dotenv=["CLOUDINARY_"]),
    Rule("minio", "MinIO", "storage", dependencies=[npm("minio"), docker("minio/minio")]),

    # ── AI / ML ────────────────────────────────────────────
    Rule("openai", "OpenAI", "ai", dependencies=[npm("openai"), pip_dep("openai"), gomod("github.com/sashabaranov/go-openai")], dotenv=["OPENAI_"]),
    Rule("anthropic", "Anthropic", "ai", dependencies=[npm("@anthropic-ai/sdk"), pip_dep("anthropic")], dotenv=["ANTHROPIC_"]),
    Rule("google-ai", "Google AI / Gemini", "ai", dependencies=[npm("@google/generative-ai"), pip_dep("google-generativeai")], dotenv=["GOOGLE_AI_", "GEMINI_"]),
    Rule("cohere", "Cohere", "ai", dependencies=[npm("cohere-ai"), pip_dep("cohere")], dotenv=["COHERE_"]),
    Rule("huggingface", "Hugging Face", "ai", dependencies=[npm("@huggingface/inference"), pip_dep("transformers"), pip_dep("huggingface_hub")], dotenv=["HUGGINGFACE_", "HF_"]),
    Rule("replicate", "Replicate", "ai", dependencies=[npm("replicate"), pip_dep("replicate")], dotenv=["REPLICATE_"]),
    Rule("langchain", "LangChain", "ai", dependencies=[npm("langchain"), pip_dep("langchain")], dotenv=["LANGCHAIN_"]),
    Rule("llamaindex", "LlamaIndex", "ai", dependencies=[npm("llamaindex"), pip_dep("llama-index")]),
    Rule("vercel-ai", "Vercel AI SDK", "ai", dependencies=[npm("ai"), npm("@ai-sdk/openai")]),
    Rule("ollama", "Ollama", "ai", dependencies=[npm("ollama"), pip_dep("ollama")], dotenv=["OLLAMA_"]),
    Rule("mistral", "Mistral AI", "ai", dependencies=[npm("@mistralai/mistralai"), pip_dep("mistralai")], dotenv=["MISTRAL_"]),
    Rule("groq", "Groq", "ai", dependencies=[npm("groq-sdk"), pip_dep("groq")], dotenv=["GROQ_"]),
    Rule("deepseek", "DeepSeek", "ai", dependencies=[npm("deepseek"), pip_dep("deepseek")], dotenv=["DEEPSEEK_"]),
    Rule("xai", "xAI", "ai", dependencies=[npm("@x-ai/sdk")], dotenv=["XAI_"]),
    Rule("elevenlabs", "ElevenLabs", "ai", dependencies=[npm("elevenlabs"), pip_dep("elevenlabs")], dotenv=["ELEVENLABS_"]),
    Rule("tensorflow", "TensorFlow", "ai", dependencies=[npm("@tensorflow/tfjs"), pip_dep("tensorflow")]),
    Rule("pytorch", "PyTorch", "ai", dependencies=[pip_dep("torch"), pip_dep("pytorch")]),
    Rule("aws-bedrock", "AWS Bedrock", "ai", dependencies=[npm("@aws-sdk/client-bedrock-runtime")], dotenv=["BEDROCK_"]),
    Rule("azure-openai", "Azure OpenAI", "ai", dependencies=[npm("@azure/openai")], dotenv=["AZURE_OPENAI_"]),

    # ── ANALYTICS ──────────────────────────────────────────
    Rule("google-analytics", "Google Analytics", "analytics", dependencies=[npm("react-ga"), npm("react-ga4")], dotenv=["GA_", "GOOGLE_ANALYTICS_"]),
    Rule("posthog", "PostHog", "analytics", dependencies=[npm("posthog-js"), npm("posthog-node"), pip_dep("posthog")], dotenv=["POSTHOG_", "NEXT_PUBLIC_POSTHOG_"]),
    Rule("segment", "Segment", "analytics", dependencies=[npm("@segment/analytics-next"), npm("analytics-node")], dotenv=["SEGMENT_"]),
    Rule("mixpanel", "Mixpanel", "analytics", dependencies=[npm("mixpanel"), npm("mixpanel-browser")], dotenv=["MIXPANEL_"]),
    Rule("amplitude", "Amplitude", "analytics", dependencies=[npm("@amplitude/analytics-browser"), npm("@amplitude/analytics-node")], dotenv=["AMPLITUDE_"]),
    Rule("plausible", "Plausible", "analytics", dependencies=[npm("plausible-tracker")], dotenv=["PLAUSIBLE_"]),
    Rule("hotjar", "Hotjar", "analytics", dependencies=[npm("@hotjar/browser")]),
    Rule("fathom", "Fathom", "analytics", dependencies=[npm("fathom-client")], dotenv=["FATHOM_"]),
    Rule("vercel-analytics", "Vercel Analytics", "analytics", dependencies=[npm("@vercel/analytics")]),

    # ── MONITORING / OBSERVABILITY ─────────────────────────
    Rule("sentry", "Sentry", "monitoring", _m(files=[".sentryclirc"]), dependencies=[npm("@sentry/node"), npm("@sentry/browser"), npm("@sentry/react"), npm("@sentry/nextjs"), pip_dep("sentry-sdk"), cargo("sentry"), gem("sentry-ruby")], dotenv=["SENTRY_"]),
    Rule("datadog", "Datadog", "monitoring", dependencies=[npm("dd-trace"), pip_dep("ddtrace")], dotenv=["DD_", "DATADOG_"]),
    Rule("newrelic", "New Relic", "monitoring", _m(files=["newrelic.js", "newrelic.yml"]), dependencies=[npm("newrelic"), pip_dep("newrelic")], dotenv=["NEW_RELIC_", "NEWRELIC_"]),
    Rule("opentelemetry", "OpenTelemetry", "monitoring", dependencies=[npm("@opentelemetry/api"), npm("@opentelemetry/sdk-node"), pip_dep("opentelemetry-api")], dotenv=["OTEL_"]),
    Rule("prometheus", "Prometheus", "monitoring", dependencies=[npm("prom-client"), docker("prom/prometheus")]),
    Rule("grafana", "Grafana", "monitoring", dependencies=[docker("grafana/grafana")], dotenv=["GRAFANA_"]),
    Rule("logrocket", "LogRocket", "monitoring", dependencies=[npm("logrocket")], dotenv=["LOGROCKET_"]),
    Rule("bugsnag", "Bugsnag", "monitoring", dependencies=[npm("@bugsnag/js"), npm("@bugsnag/react")], dotenv=["BUGSNAG_"]),
    Rule("rollbar", "Rollbar", "monitoring", dependencies=[npm("rollbar"), pip_dep("rollbar")], dotenv=["ROLLBAR_"]),
    Rule("pagerduty", "PagerDuty", "monitoring", dependencies=[npm("@pagerduty/pdjs")], dotenv=["PAGERDUTY_"]),
    Rule("betterstack", "Better Stack", "monitoring", dependencies=[npm("@logtail/node")], dotenv=["LOGTAIL_", "BETTERSTACK_"]),
    Rule("honeybadger", "Honeybadger", "monitoring", dependencies=[npm("@honeybadger-io/js")], dotenv=["HONEYBADGER_"]),

    # ── AUTH ───────────────────────────────────────────────
    Rule("auth0", "Auth0", "auth", dependencies=[npm("@auth0/nextjs-auth0"), npm("auth0"), npm("@auth0/auth0-react")], dotenv=["AUTH0_"]),
    Rule("clerk", "Clerk", "auth", dependencies=[npm("@clerk/nextjs"), npm("@clerk/clerk-react")], dotenv=["CLERK_", "NEXT_PUBLIC_CLERK_"]),
    Rule("nextauth", "NextAuth.js / Auth.js", "auth", dependencies=[npm("next-auth"), npm("@auth/core")]),
    Rule("supabase-auth", "Supabase Auth", "auth", dependencies=[npm("@supabase/auth-helpers-nextjs"), npm("@supabase/ssr")]),
    Rule("firebase-auth", "Firebase Auth", "auth", dependencies=[npm("firebase/auth"), npm("@react-firebase/auth")]),
    Rule("okta", "Okta", "auth", dependencies=[npm("@okta/okta-react"), npm("@okta/okta-auth-js")], dotenv=["OKTA_"]),
    Rule("kinde", "Kinde", "auth", dependencies=[npm("@kinde-oss/kinde-auth-nextjs")], dotenv=["KINDE_"]),
    Rule("better-auth", "Better Auth", "auth", dependencies=[npm("better-auth")]),
    Rule("logto", "Logto", "auth", dependencies=[npm("@logto/next")], dotenv=["LOGTO_"]),
    Rule("cognito", "AWS Cognito", "auth", dependencies=[npm("@aws-sdk/client-cognito-identity-provider")], dotenv=["COGNITO_"]),
    Rule("keycloak", "Keycloak", "auth", dependencies=[npm("keycloak-js"), docker("keycloak/keycloak")], dotenv=["KEYCLOAK_"]),

    # ── PAYMENT ────────────────────────────────────────────
    Rule("stripe", "Stripe", "payment", dependencies=[npm("stripe"), npm("@stripe/stripe-js"), pip_dep("stripe"), gem("stripe"), gomod("github.com/stripe/stripe-go")], dotenv=["STRIPE_"]),
    Rule("paypal", "PayPal", "payment", dependencies=[npm("@paypal/checkout-server-sdk"), npm("@paypal/react-paypal-js")], dotenv=["PAYPAL_"]),
    Rule("paddle", "Paddle", "payment", dependencies=[npm("@paddle/paddle-js")], dotenv=["PADDLE_"]),
    Rule("lemon-squeezy", "Lemon Squeezy", "payment", dependencies=[npm("@lemonsqueezy/lemonsqueezy.js")], dotenv=["LEMONSQUEEZY_"]),
    Rule("razorpay", "Razorpay", "payment", dependencies=[npm("razorpay")], dotenv=["RAZORPAY_"]),

    # ── NOTIFICATION / EMAIL ───────────────────────────────
    Rule("sendgrid", "SendGrid", "notification", dependencies=[npm("@sendgrid/mail")], dotenv=["SENDGRID_"]),
    Rule("resend", "Resend", "notification", dependencies=[npm("resend")], dotenv=["RESEND_"]),
    Rule("mailgun", "Mailgun", "notification", dependencies=[npm("mailgun.js"), npm("mailgun-js")], dotenv=["MAILGUN_"]),
    Rule("twilio", "Twilio", "notification", dependencies=[npm("twilio"), pip_dep("twilio")], dotenv=["TWILIO_"]),
    Rule("postmark", "Postmark", "notification", dependencies=[npm("postmark")], dotenv=["POSTMARK_"]),
    Rule("ses", "AWS SES", "notification", dependencies=[npm("@aws-sdk/client-ses")], dotenv=["SES_"]),
    Rule("novu", "Novu", "notification", dependencies=[npm("@novu/node")], dotenv=["NOVU_"]),

    # ── CMS ────────────────────────────────────────────────
    Rule("strapi", "Strapi", "cms", dependencies=[npm("@strapi/strapi")]),
    Rule("sanity", "Sanity", "cms", dependencies=[npm("@sanity/client"), npm("sanity")], dotenv=["SANITY_", "NEXT_PUBLIC_SANITY_"]),
    Rule("contentful", "Contentful", "cms", dependencies=[npm("contentful")], dotenv=["CONTENTFUL_"]),
    Rule("wordpress", "WordPress", "cms", _m(files=["wp-config.php", "wp-content"])),
    Rule("payload-cms", "Payload CMS", "cms", dependencies=[npm("payload")]),
    Rule("ghost", "Ghost", "cms", dependencies=[npm("@tryghost/content-api")]),
    Rule("datocms", "DatoCMS", "cms", dependencies=[npm("react-datocms")], dotenv=["DATOCMS_", "DATO_"]),
    Rule("storyblok", "Storyblok", "cms", dependencies=[npm("@storyblok/react")], dotenv=["STORYBLOK_"]),
    Rule("directus", "Directus", "cms", dependencies=[npm("@directus/sdk")]),
    Rule("keystone", "Keystone", "cms", dependencies=[npm("@keystone-6/core")]),
    Rule("shopify", "Shopify", "cms", dependencies=[npm("@shopify/shopify-api"), npm("@shopify/hydrogen")], dotenv=["SHOPIFY_"]),

    # ── SECURITY ───────────────────────────────────────────
    Rule("snyk", "Snyk", "security", _m(files=[".snyk"])),
    Rule("vault", "HashiCorp Vault", "security", dependencies=[npm("node-vault"), docker("hashicorp/vault")], dotenv=["VAULT_"]),
    Rule("infisical", "Infisical", "security", _m(files=[".infisical.json"]), dependencies=[npm("@infisical/sdk")], dotenv=["INFISICAL_"]),
    Rule("gitguardian", "GitGuardian", "security", _m(files=[".gitguardian.yml"])),

    # ── AUTOMATION ─────────────────────────────────────────
    Rule("puppeteer-auto", "Puppeteer", "automation", dependencies=[npm("puppeteer")]),
    Rule("playwright-auto", "Playwright", "automation", dependencies=[npm("playwright"), pip_dep("playwright")]),
    Rule("n8n", "n8n", "automation", dependencies=[npm("n8n"), docker("n8nio/n8n")]),
    Rule("inngest", "Inngest", "automation", dependencies=[npm("inngest")]),
    Rule("temporal", "Temporal", "automation", dependencies=[npm("@temporalio/client"), pip_dep("temporalio")]),
    Rule("trigger-dev", "Trigger.dev", "automation", dependencies=[npm("@trigger.dev/sdk")]),

    # ── SAAS / MISC TOOLS ─────────────────────────────────
    Rule("socketio", "Socket.IO", "tool", dependencies=[npm("socket.io"), npm("socket.io-client")]),
    Rule("trpc", "tRPC", "tool", dependencies=[npm("@trpc/server"), npm("@trpc/client")]),
    Rule("graphql", "GraphQL", "tool", dependencies=[npm("graphql"), npm("@apollo/client"), npm("urql")]),
    Rule("openapi", "OpenAPI", "tool", _m(files=["openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json"])),
    Rule("grpc", "gRPC", "tool", dependencies=[npm("@grpc/grpc-js"), pip_dep("grpcio")]),
    Rule("mcp", "Model Context Protocol", "tool", dependencies=[npm("@modelcontextprotocol/sdk"), pip_dep("mcp")]),
    Rule("react-email", "React Email", "tool", dependencies=[npm("@react-email/components"), npm("react-email")]),
    Rule("launchdarkly", "LaunchDarkly", "saas", dependencies=[npm("@launchdarkly/node-server-sdk")], dotenv=["LAUNCHDARKLY_"]),
    Rule("figma", "Figma", "saas", dependencies=[npm("figma-api")], dotenv=["FIGMA_"]),

    # ── PACKAGE MANAGERS ───────────────────────────────────
    Rule("npm", "npm", "package_manager", _m(files=["package-lock.json"])),
    Rule("yarn", "Yarn", "package_manager", _m(files=["yarn.lock"])),
    Rule("pnpm", "pnpm", "package_manager", _m(files=["pnpm-lock.yaml", "pnpm-workspace.yaml"])),
    Rule("bun-pkg", "Bun", "package_manager", _m(files=["bun.lockb", "bunfig.toml"])),
    Rule("cargo-pkg", "Cargo", "package_manager", _m(files=["Cargo.lock"])),
    Rule("pip-pkg", "pip", "package_manager", _m(files=["requirements.txt"])),
    Rule("poetry", "Poetry", "package_manager", _m(files=["poetry.lock"]), dependencies=[pip_dep("poetry")]),
    Rule("pipenv", "Pipenv", "package_manager", _m(files=["Pipfile.lock"])),
    Rule("bundler", "Bundler", "package_manager", _m(files=["Gemfile.lock"])),
    Rule("composer-pkg", "Composer", "package_manager", _m(files=["composer.lock"])),

    # ── RUNTIME ────────────────────────────────────────────
    Rule("nodejs", "Node.js", "runtime", _m(files=["package.json", ".nvmrc", ".node-version"])),
    Rule("deno", "Deno", "runtime", _m(files=["deno.json", "deno.jsonc", "deno.lock"])),
    Rule("bun-rt", "Bun", "runtime", _m(files=["bun.lockb", "bunfig.toml"])),

    # ── APP / INFRASTRUCTURE IMAGES ────────────────────────
    Rule("nginx", "Nginx", "app", _m(files=["nginx.conf"]), dependencies=[docker("nginx")]),
    Rule("caddy", "Caddy", "app", _m(files=["Caddyfile"]), dependencies=[docker("caddy")]),
    Rule("traefik", "Traefik", "app", dependencies=[docker("traefik")]),
    Rule("kong", "Kong", "app", dependencies=[docker("kong")]),
    Rule("haproxy", "HAProxy", "app", dependencies=[docker("haproxy")]),
    Rule("vault-app", "HashiCorp Vault", "app", dependencies=[docker("hashicorp/vault")]),
    Rule("consul", "Consul", "app", dependencies=[docker("consul")]),
    Rule("zookeeper", "Zookeeper", "app", dependencies=[docker("zookeeper")]),
    Rule("kibana", "Kibana", "app", dependencies=[docker("kibana")]),
]
