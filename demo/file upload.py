from hstream import hs

hs.markdown("# upload")
uploaded_file = hs.file_upload("Upload your file")

if uploaded_file and hs.button("Process and Download"):
    hs.markdown("uploaded")

hs.markdown(uploaded_file)
