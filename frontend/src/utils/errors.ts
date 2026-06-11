import { ApiError } from "../api/client";

const COLLECTION_ERROR_MESSAGE =
  "Não foi possível coletar essa página. Alguns sites bloqueiam leitura automática. Tente um RSS.";

export function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.code === "blocked_url") {
      return "URL bloqueada por segurança.";
    }

    if (error.code === "invalid_url") {
      return "URL inválida.";
    }

    if (["fetch_failed", "fetch_timeout", "empty_content"].includes(error.code)) {
      return COLLECTION_ERROR_MESSAGE;
    }

    return error.message;
  }

  if (error instanceof TypeError) {
    return "Nao foi possivel conectar com a API.";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado.";
}
