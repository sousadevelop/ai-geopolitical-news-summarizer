type LoadingStateProps = {
  label?: string;
};

export function LoadingState({ label = "Carregando dados" }: LoadingStateProps) {
  return (
    <div className="state-block" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
