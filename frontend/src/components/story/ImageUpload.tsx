import React, { useRef, useState, useEffect, useMemo } from 'react';
import { Upload, Image as ImageIcon, X, RefreshCw, AlertCircle } from 'lucide-react';

interface ImageUploadProps {
  file: File | null;
  onSelectFile: (file: File | null) => void;
  disabled?: boolean;
}

const MAX_IMAGE_BYTES = 5 * 1024 * 1024; // 5 MB limit
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp'];

export const ImageUpload: React.FC<ImageUploadProps> = ({
  file,
  onSelectFile,
  disabled = false,
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Derive preview URL directly from file prop without cascading state renders
  const previewUrl = useMemo(() => {
    if (!file) return null;
    return URL.createObjectURL(file);
  }, [file]);

  // Clean up previous object URL whenever file changes or component unmounts
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleValidateAndSelect = (selectedFile: File) => {
    setValidationError(null);

    // 1. Validate MIME type
    if (!ALLOWED_TYPES.includes(selectedFile.type.toLowerCase())) {
      setValidationError('Unsupported format. Please upload a PNG, JPEG, or WEBP image.');
      return;
    }

    // 2. Validate maximum file size (5 MB)
    if (selectedFile.size > MAX_IMAGE_BYTES) {
      const sizeMb = (selectedFile.size / (1024 * 1024)).toFixed(1);
      setValidationError(`Image is too large (${sizeMb} MB). Maximum allowed size is 5 MB.`);
      return;
    }

    onSelectFile(selectedFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      handleValidateAndSelect(selected);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      handleValidateAndSelect(droppedFile);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelectFile(null);
    setValidationError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(0)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 font-serif text-base sm:text-[17px] font-extrabold text-[#2B1B2A] tracking-tight">
          <ImageIcon className="h-4.5 w-4.5 text-[#9C8EB9]" />
          <span>Visual Inspiration</span>
        </label>
        <span className="font-sans text-xs font-normal text-[#8A7988]">PNG, JPG, WEBP • Up to 5 MB</span>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleFileChange}
        disabled={disabled}
        className="hidden"
        aria-label="Upload visual inspiration image"
      />

      {/* Validation error notice */}
      {validationError && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700 animate-in fade-in">
          <AlertCircle className="h-3.5 w-3.5 shrink-0 text-rose-500" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Upload Dropzone or Selected Preview */}
      {file && previewUrl ? (
        <div className="flex flex-col sm:flex-row items-center gap-4 rounded-2xl border border-[#E4DDD4] bg-[#FCFBF9] p-3.5 shadow-2xs">
          <div className="relative h-24 w-28 shrink-0 overflow-hidden rounded-xl border border-[#EAE2D8] bg-[#F7F2EC]">
            <img
              src={previewUrl}
              alt="Visual inspiration preview"
              className="h-full w-full object-cover"
            />
          </div>

          <div className="flex-1 min-w-0 text-left space-y-1">
            <p className="font-serif text-sm font-medium text-[#352033] truncate">
              {file.name}
            </p>
            <p className="text-xs text-[#7A6C79]">
              {formatFileSize(file.size)} • Ready to inspire your story
            </p>
            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                disabled={disabled}
                onClick={() => inputRef.current?.click()}
                className="inline-flex items-center gap-1 text-xs text-[#C9593E] hover:text-[#9E3F27] font-medium transition-colors cursor-pointer disabled:opacity-50"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Replace</span>
              </button>
              <span className="text-[#D6C7B9]">•</span>
              <button
                type="button"
                disabled={disabled}
                onClick={handleRemove}
                className="inline-flex items-center gap-1 text-xs text-rose-600 hover:text-rose-800 transition-colors cursor-pointer disabled:opacity-50"
              >
                <X className="h-3 w-3" />
                <span>Remove</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div
          onClick={() => !disabled && inputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`flex flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed p-6 sm:p-7 text-center transition-all cursor-pointer ${
            isDragging
              ? 'border-[#D96B50] bg-[#FAF3EC]'
              : 'border-[#E4DDD4] bg-[#FCFBF9] hover:border-[#D4C3B7] hover:bg-[#FAF7F2]'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#FAF0EB] text-[#D96B50]">
            <Upload className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <p className="font-serif text-sm font-medium text-[#352033]">
              A picture can tell a thousand stories.
            </p>
            <p className="text-xs text-[#7A6C79]">
              Drop an image here or <span className="text-[#C9593E] font-medium underline">browse</span> to upload
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
