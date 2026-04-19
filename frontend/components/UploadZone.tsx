"use client";

import { useCallback } from "react";

import { FileAudio2, FileImage, FileText, Upload } from "lucide-react";
import { useDropzone } from "react-dropzone";

type UploadZoneProps = {
  file: File | null;
  onFileSelect: (file: File | null) => void;
};

function labelForFile(file: File): string {
  if (file.type.includes("pdf")) return "PDF manual";
  if (file.type.startsWith("image/")) return "Image query";
  if (file.type.startsWith("audio/")) return "Voice note";
  return "Uploaded file";
}

function iconForFile(file: File) {
  if (file.type.includes("pdf")) return FileText;
  if (file.type.startsWith("image/")) return FileImage;
  if (file.type.startsWith("audio/")) return FileAudio2;
  return Upload;
}

export function UploadZone({ file, onFileSelect }: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFileSelect(acceptedFiles[0] ?? null);
    },
    [onFileSelect],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    maxFiles: 1,
    onDrop,
  });

  const SelectedIcon = file ? iconForFile(file) : Upload;

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={`flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed p-6 text-center transition ${
          isDragActive ? "border-emerald-400 bg-emerald-500/10" : "border-zinc-700 bg-zinc-900"
        }`}
      >
        <input {...getInputProps()} />
        <SelectedIcon className="mb-3 h-8 w-8 text-zinc-400" />
        <p className="text-sm font-medium">Drop PDF, image, or WAV</p>
        <p className="mt-1 text-sm text-zinc-500">Or click to browse local files</p>
      </div>
      {file ? (
        <div className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm">
          <div>
            <p className="font-medium text-zinc-100">{labelForFile(file)}</p>
            <p className="text-zinc-500">{file.name}</p>
          </div>
          <button
            className="text-zinc-400 transition hover:text-zinc-200"
            onClick={() => {
              onFileSelect(null);
            }}
            type="button"
          >
            Clear
          </button>
        </div>
      ) : null}
    </div>
  );
}
