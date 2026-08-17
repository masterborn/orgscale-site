// Local stand-in for https://edit.framer.com/init.mjs
//
// Framer's floating "Editor Bar" only ever renders for a signed-in editor of
// the original Framer project, so on a self-hosted copy it can never show
// anything -- it just triggers a cross-origin request that fails. This stub
// satisfies the dynamic import with a component that renders nothing.
export function createEditorBar() {
  return function EditorBar() {
    return null;
  };
}
export default createEditorBar;
