# Research Assistant Frontend

A minimalistic Next.js frontend for the Research Assistant API that allows users to ask natural language questions and get AI-powered answers from scientific literature.

## 🚀 Features

- **Simple UI**: Clean, minimalistic design with Tailwind CSS
- **Natural Language Questions**: Users can ask questions in plain English
- **AI-Powered Answers**: Uses OpenAI GPT-4 to generate comprehensive answers
- **Source Citations**: Shows relevant research paper chunks with links
- **Responsive Design**: Works on desktop and mobile
- **Real-time Search**: Integrates with the backend similarity search API

## 📋 Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`
- OpenAI API key

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Copy the environment example file:
```bash
cp env.example .env.local
```

Edit `.env.local` and add your OpenAI API key:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4

# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 🔧 How It Works

1. **User Input**: User enters a natural language question
2. **Backend Search**: Frontend calls the backend `/api/similarity_search` endpoint
3. **Context Preparation**: Relevant research paper chunks are formatted as context
4. **AI Generation**: OpenAI GPT-4 generates a comprehensive answer using the context
5. **Display Results**: Answer is displayed along with source citations

## 📁 Project Structure

```
frontend/
├── package.json              # Dependencies and scripts
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── env.example               # Environment variables template
└── src/
    ├── app/
    │   ├── globals.css       # Global styles
    │   ├── layout.tsx        # Root layout
    │   ├── page.tsx          # Main page
    │   └── api/
    │       └── chat/
    │           └── route.ts  # API route for chat
    ├── components/
    │   ├── SearchForm.tsx    # Search input form
    │   ├── SearchResults.tsx # Results display
    │   └── LoadingSpinner.tsx # Loading indicator
    ├── lib/
    │   └── openai.ts         # OpenAI utility functions
    └── types/
        └── index.ts          # TypeScript type definitions
```

## 🎨 UI Components

### SearchForm
- Input field for natural language questions
- Example questions for user guidance
- Submit button with loading state

### SearchResults
- AI-generated answer display
- Source citations with links
- Similarity scores for each source

### LoadingSpinner
- Visual feedback during processing
- Animated spinner component

## 🔌 API Integration

The frontend integrates with two APIs:

1. **Backend Research API** (`http://localhost:8000`)
   - `/api/similarity_search` - Find relevant research papers

2. **OpenAI API** (`https://api.openai.com`)
   - `/v1/chat/completions` - Generate AI answers

## 📝 Example Usage

1. Start the backend API server
2. Start the frontend development server
3. Open `http://localhost:3000`
4. Ask questions like:
   - "What is velvet bean and what are its benefits?"
   - "How does the attention mechanism work in transformers?"
   - "What are the applications of neural networks in agriculture?"

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding New Features

The codebase is structured for easy extension:
- Add new components in `src/components/`
- Add new API routes in `src/app/api/`
- Add new types in `src/types/`
- Add utility functions in `src/lib/`

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Run `npm install` to install dependencies

2. **API connection errors**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS settings in backend

3. **OpenAI API errors**
   - Verify API key in `.env.local`
   - Check API quota and billing

4. **Build errors**
   - Ensure all environment variables are set
   - Run `npm run build` to check for issues

### Environment Variables

Make sure these are set in `.env.local`:
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - OpenAI model (default: gpt-4)
- `NEXT_PUBLIC_API_BASE_URL` - Backend API URL

## 📦 Dependencies

### Production Dependencies
- `next` - React framework
- `react` & `react-dom` - React library
- `lucide-react` - Icon library
- TypeScript support included

### Development Dependencies
- `tailwindcss` - CSS framework
- `eslint` - Code linting
- `typescript` - Type checking
- `autoprefixer` & `postcss` - CSS processing

## 🚀 Deployment

For production deployment:

1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

3. Configure environment variables for production
4. Ensure backend API is accessible from production environment

## 📄 License

This project is part of the Research Assistant system. 