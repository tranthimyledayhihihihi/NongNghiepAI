import { Upload, X } from 'lucide-react';

const ImageUpload = ({ preview, onFileSelect, onClear }) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
      {preview ? (
        <div className="space-y-4">
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 mx-auto rounded"
            />
            <button
              onClick={onClear}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-600 text-center">
            Click vào nút X để xóa và chọn ảnh khác
          </p>
        </div>
      ) : (
        <div className="text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label
              htmlFor="file-upload"
              className="cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500"
            >
              <span>Chọn ảnh</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                accept="image/*"
                onChange={handleFileChange}
              />
            </label>
            <p className="text-xs text-gray-500 mt-2">
              PNG, JPG, JPEG tối đa 10MB
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
