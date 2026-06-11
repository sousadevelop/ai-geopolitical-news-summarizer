import { describe, expect, it } from "vitest";
import { ApiError } from "../api/client";
import { getErrorMessage } from "./errors";

describe("getErrorMessage", () => {
  it.each([
    ["blocked_url", "URL bloqueada por segurança."],
    ["invalid_url", "URL inválida."],
  ])("maps %s API errors", (code, expectedMessage) => {
    const error = new ApiError(400, { code, message: "Mensagem original da API." });

    expect(getErrorMessage(error)).toBe(expectedMessage);
  });

  it.each(["fetch_failed", "fetch_timeout", "empty_content"])(
    "maps %s to the collection guidance",
    (code) => {
      const error = new ApiError(502, { code, message: "Falha original." });

      expect(getErrorMessage(error)).toBe(
        "Não foi possível coletar essa página. Alguns sites bloqueiam leitura automática. Tente um RSS.",
      );
    },
  );

  it("preserves the API message for other ApiError codes", () => {
    const error = new ApiError(500, {
      code: "analysis_failed",
      message: "A análise não pôde ser concluída.",
    });

    expect(getErrorMessage(error)).toBe("A análise não pôde ser concluída.");
  });
});
