import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import { sql } from "drizzle-orm";
import {
  sqliteTable,
  text,
  integer,
  blob,
  primaryKey,
} from "drizzle-orm/sqlite-core";

// Enums matching Python
export const JobType = {
  ETL: "etl",
  RETL: "retl",
} as const;

export const ConnectionType = {
  REDSHIFT: "redshift",
  POSTGRES: "postgres",
  MYSQL: "mysql",
  MSSQL: "mssql",
  ORACLE: "oracle",
  DSQL: "dsql",
} as const;

export const HumanReadableName = {
  EMR_APP: "EMR App",
  GLUE_JOB_BUCKET: "Glue Job Bucket",
  S3_TABLE_BUCKET: "S3 Table Bucket",
  S3_TABLE_NAMESPACE: "S3 Table Namespace",
  GLUE_ROLE: "Glue Role",
  EMR_ROLE: "EMR Role",
  EMR_CLUSTER: "EMR Cluster",
  EMR_STUDIO: "EMR Studio",
} as const;

type JobTypeValues = (typeof JobType)[keyof typeof JobType];
type ConnectionTypeValues =
  (typeof ConnectionType)[keyof typeof ConnectionType];
type HumanReadableNameValues =
  (typeof HumanReadableName)[keyof typeof HumanReadableName];

interface TableSchema {
  columns: {
    name: string;
    type: string;
    nullable: boolean;
  }[];
}

interface ConnectionProperties {
  host?: string;
  port?: number;
  database?: string;
  schema?: string;
  [key: string]: unknown;
}

// Schema definitions
export const s3DataTables = sqliteTable("s3_data_tables", {
  id: integer("id").primaryKey(),
  name: text("name").unique().notNull(),
  schema: blob("schema", { mode: "json" }).$type<TableSchema>(),
});

export const emrJobScripts = sqliteTable("emr_job_scripts", {
  id: integer("id").primaryKey(),
  name: text("name").unique().notNull(),
  s3Path: text("s3_path").notNull(),
  bucket: text("bucket").notNull(),
});

export const emrJobs = sqliteTable("emr_jobs", {
  id: integer("id").primaryKey(),
  name: text("name").unique().notNull(),
  jobType: text("job_type").$type<JobTypeValues>().notNull(),
  connectionName: text("connection_name"),
  connectionType: text("connection_type").$type<ConnectionTypeValues>(),
  connectionProperties: blob("connection_properties", {
    mode: "json",
  }).$type<ConnectionProperties>(),
  sqlTable: text("sql_table"),
  incrementalColumn: text("incremental_column"),
  isFullLoad: integer("is_full_load", { mode: "boolean" }),
  scriptId: integer("script_id").references(() => emrJobScripts.id),
  requirements: text("requirements"),
});

export const emrJobInputTables = sqliteTable(
  "emr_job_input_tables",
  {
    jobId: integer("job_id").references(() => emrJobs.id),
    tableId: integer("table_id").references(() => s3DataTables.id),
  },
  (t) => ({
    pk: primaryKey(t.jobId, t.tableId),
  })
);

export const emrJobOutputTables = sqliteTable(
  "emr_job_output_tables",
  {
    jobId: integer("job_id").references(() => emrJobs.id),
    tableId: integer("table_id").references(() => s3DataTables.id),
  },
  (t) => ({
    pk: primaryKey(t.jobId, t.tableId),
  })
);

export const awsResources = sqliteTable("aws_resources", {
  id: integer("id").primaryKey(),
  name: text("name").unique().notNull(),
  humanReadableName: text("human_readable_name")
    .$type<HumanReadableNameValues>()
    .notNull(),
  resourceType: text("resource_type").notNull(),
  resourceId: text("resource_id").notNull(),
  resourceArn: text("resource_arn").notNull(),
});

// Schema object
export const schema = {
  s3DataTables,
  emrJobs,
  emrJobInputTables,
  emrJobOutputTables,
  awsResources,
  emrJobScripts,
} as const;

// Database connection
const sqlite = new Database("nextdata.db");
export const db = drizzle(sqlite, { schema });

// Helper types
export type S3DataTable = typeof s3DataTables.$inferSelect;
export type EmrJob = typeof emrJobs.$inferSelect;
export type EmrJobScript = typeof emrJobScripts.$inferSelect;
export type AwsResource = typeof awsResources.$inferSelect;
