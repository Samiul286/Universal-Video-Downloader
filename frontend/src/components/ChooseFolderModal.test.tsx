/**
 * FE-C4 (partial): Choose folder modal — "Choose folder to save"; path input; Use this folder calls onChoose.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChooseFolderModal } from './ChooseFolderModal'

describe('ChooseFolderModal', () => {
  it('shows title and path input', () => {
    render(<ChooseFolderModal onChoose={() => {}} onClose={() => {}} />)
    expect(screen.getByText(/choose folder to save/i)).toBeInTheDocument()
    const input = screen.getByPlaceholderText(/C:\\Users/)
    expect(input).toBeInTheDocument()
  })

  it('Use this folder disabled when path empty', () => {
    render(<ChooseFolderModal onChoose={() => {}} onClose={() => {}} />)
    expect(screen.getByRole('button', { name: /use this folder/i })).toBeDisabled()
  })

  it('calls onChoose with path when Use this folder clicked', async () => {
    const onChoose = vi.fn()
    render(<ChooseFolderModal onChoose={onChoose} onClose={() => {}} />)
    await userEvent.type(screen.getByPlaceholderText(/C:\\Users/), 'C:\\Videos')
    await userEvent.click(screen.getByRole('button', { name: /use this folder/i }))
    expect(onChoose).toHaveBeenCalledWith('C:\\Videos')
  })

  it('Cancel calls onClose', async () => {
    const onClose = vi.fn()
    render(<ChooseFolderModal onChoose={() => {}} onClose={onClose} />)
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }))
    expect(onClose).toHaveBeenCalled()
  })
})
