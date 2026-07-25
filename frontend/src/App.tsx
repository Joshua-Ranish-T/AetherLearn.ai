import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { CreateProject } from '@/pages/CreateProject'
import { GenerationProgress } from '@/pages/GenerationProgress'
import { ProjectDetail } from '@/pages/ProjectDetail'
import { VideoPreview } from '@/pages/VideoPreview'
import { History } from '@/pages/History'
import { Settings } from '@/pages/Settings'
import { TutorWorkspace } from '@/pages/TutorWorkspace'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TutorWorkspace />} />
        <Route element={<Layout />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="create" element={<CreateProject />} />
          <Route path="projects/:projectId" element={<ProjectDetail />} />
          <Route path="projects/:projectId/generate" element={<GenerationProgress />} />
          <Route path="videos/:videoId" element={<VideoPreview />} />
          <Route path="history" element={<History />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="/admin/*" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
