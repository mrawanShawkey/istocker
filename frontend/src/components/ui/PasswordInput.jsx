// S — a password field with show/hide toggle. Reused in SignIn + Settings.
// I — accepts only what it needs: value, onChange, placeholder
import { useState } from 'react'

export default function PasswordInput({ value, onChange, placeholder, id }) {
  const [show, setShow] = useState(false)
  return (
    <div className="s-input-wrap">
      <input
        id={id}
        className="s-input s-input-with-icon"
        type={show ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
      />
      <button type="button" className="pw-toggle" onClick={() => setShow(s => !s)}>
        {show ? '🙈' : '👁'}
      </button>
    </div>
  )
}
