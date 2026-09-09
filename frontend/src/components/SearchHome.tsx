// 화면 1 — 검색 홈. 대형 제목 + pill 검색바 + 예시 질문 칩 + 그라데이션 장식 + 푸터.
import { useState } from 'react'
import type { DemoPreset } from '../demo/presets'

interface SearchHomeProps {
  examples: DemoPreset[]
  onSearch: (rawText: string) => void
  onPickExample: (preset: DemoPreset) => void
}

export default function SearchHome({ examples, onSearch, onPickExample }: SearchHomeProps) {
  const [value, setValue] = useState('')

  function submit() {
    const text = value.trim()
    if (text) onSearch(text)
  }

  return (
    <div className="home">
      <div className="home-deco" aria-hidden="true" />

      <div className="home-inner">
        <p className="home-eyebrow">AI Knowledge Assistant</p>
        <h1 className="home-title">무엇을 찾고 계신가요?</h1>
        <p className="home-subtitle">사내의 모든 지식에서 가장 적합한 답을 찾아드립니다.</p>

        <form
          className="searchbar"
          role="search"
          onSubmit={(e) => {
            e.preventDefault()
            submit()
          }}
        >
          <span className="searchbar-icon" aria-hidden="true">
            🔍
          </span>
          <input
            className="searchbar-input"
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="업무와 관련된 질문을 입력하세요…"
            aria-label="질문 입력"
          />
          <button
            type="submit"
            className="searchbar-submit"
            disabled={!value.trim()}
            aria-label="검색"
          >
            →
          </button>
        </form>

        <div className="examples">
          <p className="examples-label">예시 질문</p>
          {examples.map((preset) => (
            <button
              key={preset.id}
              type="button"
              className="example-chip"
              onClick={() => onPickExample(preset)}
            >
              <span>{preset.rawText}</span>
              <span className="example-chip-arrow" aria-hidden="true">
                ›
              </span>
            </button>
          ))}
        </div>
      </div>

      <p className="home-footer">Your Knowledge, Smarter with AI.</p>
    </div>
  )
}
