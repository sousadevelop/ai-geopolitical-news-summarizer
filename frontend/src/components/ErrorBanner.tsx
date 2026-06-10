type ErrorBannerProps = {
  title?: string;
  message: string;
  onRetry?: () => void;
};

export function ErrorBanner({ title = "Erro", message, onRetry }: ErrorBannerProps) {
  return (
    <div className="error-banner" role="alert">
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
      </div>
      {onRetry ? (
        <button className="button button-secondary" type="button" onClick={onRetry}>
          Tentar novamente
        </button>
      ) : null}
    </div>
  );
}
