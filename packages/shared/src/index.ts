export interface ShortLink {
  id: string;
  slug: string;
  url: string;
  userId?: string | null;
  clickCount: number;
  createdAt: string;
}

export interface CreateLinkInput {
  url: string;
  slug?: string;
}
