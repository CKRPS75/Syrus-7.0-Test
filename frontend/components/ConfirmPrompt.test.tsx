import { describe, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ConfirmPrompt from './ConfirmPrompt';

describe('ConfirmPrompt', () => {
  it('renders the route confirmation choices and icons', () => {
    const markup = renderToStaticMarkup(
      <ConfirmPrompt onAccept={vi.fn()} onReject={vi.fn()} isLoading={false} />,
    );

    expect(markup).toContain('Keep Current Route');
    expect(markup).toContain('Accept New Route');
    expect(markup).toContain('<svg');
    expect(markup).not.toContain('disabled=""');
  });

  it('disables both choices while updating', () => {
    const markup = renderToStaticMarkup(
      <ConfirmPrompt onAccept={vi.fn()} onReject={vi.fn()} isLoading />,
    );

    expect(markup).toContain('Updating...');
    expect((markup.match(/disabled=""/g) ?? [])).toHaveLength(2);
  });
});
