// 상단바 — 양 화면 공통. 좌: 브랜드(Anabada, 클릭 시 홈 복귀), 우: 계정 칩(장식).
// 계정 표시는 로그인 persona(현재 데모: DevRel). 향후 SSO 연동 시 실제 사용자로 대체.
interface HeaderProps {
  account: string
  onBrandClick: () => void
}

export default function Header({ account, onBrandClick }: HeaderProps) {
  return (
    <header className="header">
      <button type="button" className="brand" onClick={onBrandClick} aria-label="Anabada 홈으로">
        Anabada
      </button>
      <div className="account">
        <span className="account-avatar" aria-hidden="true">
          {account.charAt(0).toUpperCase()}
        </span>
        <span>{account}</span>
        <span className="account-caret" aria-hidden="true">
          ▾
        </span>
      </div>
    </header>
  )
}
