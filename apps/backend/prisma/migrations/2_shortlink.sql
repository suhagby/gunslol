-- Rename Link table to ShortLink
ALTER TABLE "Link" RENAME TO "ShortLink";
-- Rename slug unique index
ALTER INDEX "Link_slug_key" RENAME TO "ShortLink_slug_key";
-- Update Click table foreign key
ALTER TABLE "Click" RENAME COLUMN "linkId" TO "shortLinkId";
ALTER TABLE "Click" DROP CONSTRAINT "Click_linkId_fkey";
ALTER TABLE "Click" ADD CONSTRAINT "Click_shortLinkId_fkey" FOREIGN KEY ("shortLinkId") REFERENCES "ShortLink"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
