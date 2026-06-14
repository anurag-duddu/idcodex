ALTER TABLE "nodes" ADD COLUMN "slug" text NOT NULL;--> statement-breakpoint
CREATE INDEX "nodes_course_parent_idx" ON "nodes" USING btree ("course_id","parent_id");