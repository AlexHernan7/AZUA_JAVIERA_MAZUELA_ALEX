// Interfaces para noticias basadas en los schemas del backend

export interface NewsArticle {
  title: string;
  description?: string;
  url: string;
  image_url?: string;
  published_at?: string;
  source_name?: string;
  author?: string;
}

export interface NewsResponse {
  articles: NewsArticle[];
  total_results: number;
  status: string;
  message: string;
}

export interface NewsErrorResponse {
  status: string;
  message: string;
}

export interface NewsHealthCheck {
  status: string;
  message: string;
  api_connection: string;
  test_results: string;
}
