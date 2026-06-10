import { ApiError } from "../api/client";

export function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
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
