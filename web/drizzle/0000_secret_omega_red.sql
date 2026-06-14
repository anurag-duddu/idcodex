CREATE TYPE "public"."course_status" AS ENUM('active', 'inactive', 'in_development', 'merged', 'empty');--> statement-breakpoint
CREATE TYPE "public"."course_type" AS ENUM('seminar', 'workshop', 'studio');--> statement-breakpoint
CREATE TYPE "public"."node_kind" AS ENUM('folder', 'file');--> statement-breakpoint
CREATE TYPE "public"."node_status" AS ENUM('published', 'pending');--> statement-breakpoint
CREATE TYPE "public"."preview_type" AS ENUM('pdf', 'image', 'video', 'office', 'none');--> statement-breakpoint
CREATE TYPE "public"."resource_type" AS ENUM('Paper', 'Slide Deck', 'Book', 'Article', 'Tool', 'PDF', 'Other');--> statement-breakpoint
CREATE TYPE "public"."user_role" AS ENUM('viewer', 'admin');--> statement-breakpoint
CREATE TYPE "public"."user_status" AS ENUM('active', 'pending');--> statement-breakpoint
CREATE TABLE "course_people" (
	"course_id" uuid NOT NULL,
	"person_id" uuid NOT NULL,
	"role" text DEFAULT 'professor',
	CONSTRAINT "course_people_course_id_person_id_pk" PRIMARY KEY("course_id","person_id")
);
--> statement-breakpoint
CREATE TABLE "course_programs" (
	"course_id" uuid NOT NULL,
	"program_id" uuid NOT NULL,
	CONSTRAINT "course_programs_course_id_program_id_pk" PRIMARY KEY("course_id","program_id")
);
--> statement-breakpoint
CREATE TABLE "courses" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"course_number" text,
	"title" text NOT NULL,
	"former_names" text[],
	"former_course_number" text,
	"type" "course_type" NOT NULL,
	"credits" numeric(3, 1),
	"status" "course_status" DEFAULT 'active' NOT NULL,
	"overview" text,
	"objectives" text,
	"outcomes" text,
	"outline" text,
	"areas_of_practice" text[],
	"competencies" text[],
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "courses_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "nodes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"course_id" uuid NOT NULL,
	"parent_id" uuid,
	"kind" "node_kind" NOT NULL,
	"name" text NOT NULL,
	"position" integer DEFAULT 0 NOT NULL,
	"storage_key" text,
	"mime_type" text,
	"size_bytes" bigint,
	"page_count" integer,
	"preview_type" "preview_type",
	"resource_type" "resource_type",
	"author" text,
	"year" integer,
	"source_link" text,
	"description" text,
	"status" "node_status" DEFAULT 'published' NOT NULL,
	"added_by" uuid,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "people" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"title" text,
	"photo_key" text,
	"bio" text,
	CONSTRAINT "people_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "programs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	CONSTRAINT "programs_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"email" text NOT NULL,
	"name" text,
	"role" "user_role" DEFAULT 'viewer' NOT NULL,
	"status" "user_status" DEFAULT 'active' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
ALTER TABLE "course_people" ADD CONSTRAINT "course_people_course_id_courses_id_fk" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "course_people" ADD CONSTRAINT "course_people_person_id_people_id_fk" FOREIGN KEY ("person_id") REFERENCES "public"."people"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "course_programs" ADD CONSTRAINT "course_programs_course_id_courses_id_fk" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "course_programs" ADD CONSTRAINT "course_programs_program_id_programs_id_fk" FOREIGN KEY ("program_id") REFERENCES "public"."programs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "nodes" ADD CONSTRAINT "nodes_course_id_courses_id_fk" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "nodes" ADD CONSTRAINT "nodes_parent_id_nodes_id_fk" FOREIGN KEY ("parent_id") REFERENCES "public"."nodes"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "nodes" ADD CONSTRAINT "nodes_added_by_users_id_fk" FOREIGN KEY ("added_by") REFERENCES "public"."users"("id") ON DELETE set null ON UPDATE no action;