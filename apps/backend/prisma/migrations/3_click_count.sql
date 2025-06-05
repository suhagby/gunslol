-- Add clickCount column to ShortLink
ALTER TABLE "ShortLink" ADD COLUMN "clickCount" INTEGER NOT NULL DEFAULT 0;
