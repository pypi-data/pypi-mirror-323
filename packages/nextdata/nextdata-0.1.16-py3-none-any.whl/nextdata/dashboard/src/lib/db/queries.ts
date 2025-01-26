import { db } from "./index";
import { and, eq } from "drizzle-orm";
import {
  s3DataTables,
  emrJobs,
  emrJobInputTables,
  emrJobOutputTables,
  type EmrJob,
} from "./index";
import "server-only";

export async function getTableByName(tableName: string) {
  return await db.query.s3DataTables.findFirst({
    where: eq(s3DataTables.name, tableName),
  });
}

export async function getJobsForTable(tableName: string): Promise<EmrJob[]> {
  // Get jobs where this table is either an input or output
  const tableId = await db
    .select({ id: s3DataTables.id })
    .from(s3DataTables)
    .where(eq(s3DataTables.name, tableName))
    .then((rows) => rows[0]?.id);

  if (!tableId) return [];

  const inputJobs = await db
    .select({
      job: emrJobs,
    })
    .from(emrJobs)
    .innerJoin(emrJobInputTables, eq(emrJobs.id, emrJobInputTables.jobId))
    .where(eq(emrJobInputTables.tableId, tableId));

  const outputJobs = await db
    .select({
      job: emrJobs,
    })
    .from(emrJobs)
    .innerJoin(emrJobOutputTables, eq(emrJobs.id, emrJobOutputTables.jobId))
    .where(eq(emrJobOutputTables.tableId, tableId));

  // Combine and deduplicate jobs
  const allJobs = [...inputJobs, ...outputJobs];
  const uniqueJobs = Array.from(
    new Map(allJobs.map((row) => [row.job.id, row.job])).values()
  );

  return uniqueJobs;
}

export async function getAllTables() {
  return await db.select().from(s3DataTables);
}

export async function getAllJobs() {
  return await db.select().from(emrJobs);
}
