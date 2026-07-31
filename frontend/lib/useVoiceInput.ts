"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** Minimal surface of the Web Speech API that this app relies on. */
interface Recognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
}

type RecognitionConstructor = new () => Recognition;

function getConstructor(): RecognitionConstructor | undefined {
  const scope = window as unknown as {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  };
  return scope.SpeechRecognition ?? scope.webkitSpeechRecognition;
}

/**
 * Dictation for the ask bar. Returns `supported: false` on browsers without
 * the Web Speech API so the caller can hide the control entirely.
 */
export function useVoiceInput(onTranscript: (text: string) => void) {
  const [supported] = useState(() => Boolean(getConstructor()));
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<Recognition | null>(null);
  const callbackRef = useRef(onTranscript);

  // Keeps the live handler reachable from a recognition session already in flight
  useEffect(() => {
    callbackRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const toggle = useCallback(() => {
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }

    const Constructor = getConstructor();
    if (!Constructor) return;

    const recognition = new Constructor();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results, (result) => result[0].transcript)
        .join(" ")
        .trim();
      if (transcript) callbackRef.current(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }, [listening]);

  return { supported, listening, toggle };
}
